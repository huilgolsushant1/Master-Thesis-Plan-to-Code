from fastapi import FastAPI, HTTPException, Request
from crew_setup import build_crew
from utils import build_prompt_from_agents
from openai import OpenAI
from pydantic import BaseModel
from typing import List, Optional, Union
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware
import requests
from requests.auth import HTTPBasicAuth
from crewai import Crew, Task
from agents import ticket_generator_agent, development_task_extractor, frontend_task_agent, backend_task_agent, database_task_agent, cloud_task_agent, devops_task_agent, design_task_agent
import json

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
app = FastAPI()

origins = ["http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProjectInput(BaseModel):
    projectName: str
    projectDescription: str
    stakeholder: str
    category: str
    startDate: str
    expectedDuration: str
    durationUnit: str
    teamSize: str
    budget: str
    experience: str
    locationType: str
    frontend: List[str]
    backend: List[str]
    database: List[str]
    cloud: List[str]
    devops: List[str]
    design: List[str]
    otherTech: Optional[str] = None

class RefinementRequest(BaseModel):
    original_plan: str
    user_feedback: str

class JiraTicketPlanRequest(BaseModel):
    plan: str

class FinalizedTicket(BaseModel):
    summary: str
    description: str
    
class CodeSnippetSingleTaskRequest(BaseModel):
    task_name: str
    task_description: str
    final_plan: str

TICKET_STORE_PATH = "saved_tickets.json"

def save_tickets_locally(ticket_list):
    try:
        if os.path.exists(TICKET_STORE_PATH):
            with open(TICKET_STORE_PATH, "r") as f:
                existing = json.load(f)
        else:
            existing = []

        existing.extend(ticket_list)

        with open(TICKET_STORE_PATH, "w") as f:
            json.dump(existing, f, indent=2)

    except Exception as e:
        print("⚠️ Error saving tickets locally:", e)


@app.post("/api/generate-project-plan")
async def generate_project_plan(request: Request):
    try:
        data = await request.json()

        # Check if input is structured ProjectInput (by presence of projectName)
        if "projectName" in data:
            input_data = ProjectInput(**data)

        # Or if input is free-form text to parse into ProjectInput
        elif "text" in data:
            free_text = data["text"]

            # Prompt OpenAI to parse the free text into structured JSON
            prompt = f"""
You are a software project planner. Extract the following fields from the project description below and respond ONLY with valid JSON matching the structure exactly:

- projectName (string)
- projectDescription (string)
- stakeholder (string)
- category (string)
- startDate (string, e.g. "2023-01-01")
- expectedDuration (string, e.g. "4")
- durationUnit (string, e.g. "weeks")
- teamSize (string, e.g. "5")
- budget (string)
- experience (string)
- locationType (string)
- frontend (list of strings)
- backend (list of strings)
- database (list of strings)
- cloud (list of strings)
- devops (list of strings)
- design (list of strings)
- otherTech (optional string, or empty string if none)

Project description:

\"\"\"{free_text}\"\"\"
"""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert project data extractor."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0,
            )

            extracted_json_str = response.choices[0].message.content.strip()

            # Clean and parse the JSON output
            try:
                extracted_data = json.loads(extracted_json_str)
            except json.JSONDecodeError:
                # Try to clean output from markdown code fences if present
                cleaned = extracted_json_str.strip("```json").strip("```").strip()
                extracted_data = json.loads(cleaned)

            input_data = ProjectInput(**extracted_data)

        else:
            raise HTTPException(status_code=400, detail="Input must include either 'projectName' or 'text'.")

        # Now proceed with your crew/task workflow as before
        crew = build_crew(input_data)
        agent_output = crew.kickoff()

        prompt = build_prompt_from_agents(agent_output)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful and precise software architect."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )

        return {"project_plan": response.choices[0].message.content.strip()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/refine-project-plan")
async def refine_project_plan(data: RefinementRequest):
    try:
        prompt = f"""
You are a senior project planning assistant. A user has submitted feedback to refine the following project plan.

---
USER FEEDBACK:
{data.user_feedback}

---
ORIGINAL PROJECT PLAN:
{data.original_plan}

---
Apply the feedback precisely. Keep the overall structure of the document, and modify only what's necessary.
Output the full refined plan with improved clarity and consistency.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert planner and editor."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
        )

        return {"refined_plan": response.choices[0].message.content.strip()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-jira-tickets-from-plan")
async def generate_jira_tickets(data: JiraTicketPlanRequest):
    try:
        plan = data.plan
        crew = Crew(
            agents=[ticket_generator_agent],
            tasks=[
                Task(
                    agent=ticket_generator_agent,
                    description=f"Generate JIRA ticket suggestions from this plan:\n{plan}",
                    expected_output="A plain JSON list of objects — do not wrap in code fences, return ONLY JSON",
                )
            ],
            process="sequential",
            verbose=True,
        )

        output = crew.kickoff()
        raw_result = output.raw  # This is the string your agent returned
        print("✅ RAW agent output:\n", raw_result)

        # Clean and parse it
        json_start = raw_result.find("[")
        json_end = raw_result.rfind("]") + 1
        clean_output = raw_result[json_start:json_end]
        tickets = json.loads(clean_output)

        return {"tickets": tickets}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/push-finalized-tickets")
async def push_finalized_tickets(tickets: List[FinalizedTicket]):
    try:
        auth = HTTPBasicAuth(os.getenv("JIRA_EMAIL"), os.getenv("JIRA_API_TOKEN"))
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        jira_url = f"{os.getenv('JIRA_BASE_URL')}/rest/api/3/issue"

        results = []

        for ticket in tickets:
            adf_description = {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "text": ticket.description or ""}
                        ],
                    }
                ],
            }

            payload = {
                "fields": {
                    "project": {"key": os.getenv("JIRA_PROJECT_KEY")},
                    "summary": ticket.summary,
                    "description": adf_description,
                    "issuetype": {"name": "Task"},
                }
            }

            response = requests.post(jira_url, json=payload, headers=headers, auth=auth)
            if response.status_code == 201:
                issue = response.json()
                ticket_info = {
                    "summary": ticket.summary,
                    "description": ticket.description,
                    "key": issue["key"],
                    "url": f"{os.getenv('JIRA_BASE_URL')}/browse/{issue['key']}",
                }
                results.append(ticket_info)
            else:
                results.append({"summary": ticket.summary, "error": response.text})

        # 🔐 Save ticket summaries locally
        save_tickets_locally(results)

        return {"created_issues": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


from agents import development_task_extractor

@app.post("/api/get-suggested-dev-tasks")
async def get_suggested_dev_tasks(request: Request):
    try:
        data = await request.json()
        final_plan = data.get("final_plan")

        if not final_plan:
            raise HTTPException(status_code=400, detail="Missing 'final_plan' in request")

        task = Task(
            agent=development_task_extractor,
            description=f"""
        Review the following software project plan and extract only development tasks. These should be coding-related tasks that developers would need to implement — such as building APIs, setting up databases, authentication, frontend components, CI/CD, or infrastructure code.

        Avoid including planning, meetings, or stakeholder reviews.

        ### PROJECT PLAN:
        {final_plan}

        Respond ONLY with a plain JSON list like this:
        [
        {{
            "summary": "Implement OAuth2 login flow",
            "description": "Use FastAPI and Google OAuth2 to let users authenticate and retrieve a JWT token."
        }},
        ...
        ]
        """,
            expected_output="A clean JSON list of implementation tasks with summary and description."
        )

        crew = Crew(
            agents=[development_task_extractor],
            tasks=[task],
            process="sequential",
            verbose=True
        )

        output = crew.kickoff()
        raw_output = output.raw

        # Extract JSON
        json_start = raw_output.find("[")
        json_end = raw_output.rfind("]") + 1
        clean_json = raw_output[json_start:json_end]
        dev_tasks = json.loads(clean_json)

        return {"suggested_tasks": dev_tasks}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/api/generate-code-snippet")
async def generate_code_snippet(data: CodeSnippetSingleTaskRequest):
    try:
        prompt = f"""
        You are an experienced senior software engineer. Based on the project plan below, generate a code snippet that addresses the following task.

        ### PROJECT PLAN
        {data.final_plan}

        ### TASK NAME
        {data.task_name}

        ### TASK DESCRIPTION
        {data.task_description}

        ---

        Use the tech stack (e.g., frontend/backend/frameworks/database/cloud) referenced in the project plan. Your response must:
        - Be relevant to the described task.
        - Include one high-quality code snippet.
        - Include the appropriate language in your response.
        - Return ONLY a valid JSON object in the format:

        {{
        "task": "Task name",
        "language": "Python | JavaScript | SQL | etc.",
        "snippet": "your code here"
        }}
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a precise full-stack developer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )

        raw_output = response.choices[0].message.content.strip()

        try:
            return json.loads(raw_output)
        except json.JSONDecodeError:
            cleaned = raw_output.strip("```json").strip("```").strip()
            return json.loads(cleaned)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/get-dev-categories")
async def get_dev_categories(request: Request):
    try:
        data = await request.json()
        final_plan = data.get("final_plan")
        if not final_plan:
            raise HTTPException(status_code=400, detail="Missing final_plan")

        # Extract tech from plan using LLM or regex (LLM preferred for reliability)
        prompt = f"""
                Given this software project plan, extract the tech stack used across the following categories: Frontend, Backend, Database, Cloud, DevOps, Design.

                Only respond in this JSON format:
                [
                {{ "name": "Frontend", "tech": ["React", "Tailwind"] }},
                {{ "name": "Backend", "tech": ["FastAPI"] }},
                ...
                ]

                Do not explain anything. Use the technologies mentioned in the plan only.

                PROJECT PLAN:
                {final_plan}
            """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You extract categorized tech stacks from project plans."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
        )

        raw = response.choices[0].message.content.strip()
        try:
            return {"categories": json.loads(raw)}
        except json.JSONDecodeError:
            cleaned = raw.strip("```json").strip("```").strip()
            return {"categories": json.loads(cleaned)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/get-tasks-by-category")
async def get_tasks_by_category(request: Request):
    try:
        data = await request.json()
        category = data.get("category")
        final_plan = data.get("final_plan")

        if not category or not final_plan:
            raise HTTPException(status_code=400, detail="Missing category or final_plan")

        agent = {
            "Frontend": frontend_task_agent,
            "Backend": backend_task_agent,
            "Database": database_task_agent,
            "Cloud": cloud_task_agent,
            "DevOps": devops_task_agent,
            "Design": design_task_agent
        }.get(category)

        if not agent:
            raise HTTPException(status_code=400, detail=f"No agent found for category '{category}'")

        description = f"""
                        Given this software project plan, list out 5-10 specific development tasks the {category.lower()} developer should implement using the technologies mentioned in the plan. 
                        Each task should be focused (e.g., 'Build navbar', 'Integrate login form') and output as JSON like this:

                        [
                        {{ "summary": "...", "description": "..." }},
                        ...
                        ]

                        PROJECT PLAN:
                        {final_plan}
                        """

        task = Task(
            agent=agent,
            description=description,
            expected_output="A plain JSON list of dev tasks (summary + description)"
        )

        crew = Crew(agents=[agent], tasks=[task], process="sequential", verbose=True)
        output = crew.kickoff()

        raw = output.raw
        json_start = raw.find("[")
        json_end = raw.rfind("]") + 1
        clean = raw[json_start:json_end]
        return {"tasks": json.loads(clean)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
