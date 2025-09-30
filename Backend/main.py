from fastapi import FastAPI, HTTPException, Request
from crew_setup import build_crew
from utils import build_prompt_from_agents
from openai import OpenAI
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware
import requests
from requests.auth import HTTPBasicAuth
from crewai import Crew, Task
from agents import (
    ticket_generator_agent,
    development_task_extractor,
    frontend_task_agent,
    backend_task_agent,
    database_task_agent,
    cloud_task_agent,
    devops_task_agent,
    design_task_agent,
)
import json
import logging

# local import from our new helper module (that you paste as utils_free_text.py or inside utils.py)
from utils_free_text import normalize_input, run_agents_wrapper, call_llm_to_extract_json_from_free_text

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

logger = logging.getLogger(__name__)

# ------------------ DATA MODELS ------------------

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


# ------------------ ROUTES ------------------

@app.post("/api/generate-project-plan")
async def generate_project_plan(request: Request):
    """
    Unified endpoint:
    - If user posts structured fields (ProjectInput), we parse normally.
    - If user posts free-text brief ({"text": "..."}), we extract JSON using LLM.
    Both paths are normalized, passed through agents, and then final plan generated.
    """
    try:
        data = await request.json()

        # structured ProjectInput path
        if "projectName" in data:
            input_data = ProjectInput(**data)
            agent_input = normalize_input(input_data)

        # free-text path
        elif "text" in data:
            free_text = data["text"]
            agent_input = normalize_input(free_text)

        else:
            raise HTTPException(status_code=400, detail="Input must include either 'projectName' or 'text'.")

        # ---- run agents on normalized input ----
        agent_output = run_agents_wrapper(agent_input)

        # ---- build final plan prompt ----
        prompt = build_prompt_from_agents(agent_output)

        response = client.chat.completions.create(
            model="o3",
            messages=[
                {"role": "system", "content": "You are a helpful and precise software architect."},
                {"role": "user", "content": prompt},
            ]
        )

        return {"project_plan": response.choices[0].message.content.strip()}

    except Exception as e:
        logger.exception("Error in /api/generate-project-plan")
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
            model="o3",
            messages=[
                {"role": "system", "content": "You are an expert planner and editor."},
                {"role": "user", "content": prompt},
            ]
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
        raw_result = output.raw
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
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": ticket.description or ""}]}],
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
                results.append({
                    "summary": ticket.summary,
                    "description": ticket.description,
                    "key": issue["key"],
                    "url": f"{os.getenv('JIRA_BASE_URL')}/browse/{issue['key']}",
                })
            else:
                results.append({"summary": ticket.summary, "error": response.text})

        save_tickets_locally(results)
        return {"created_issues": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
Review the following project plan and extract only development tasks (APIs, DB setup, CI/CD, frontend components, etc).
Avoid planning or meetings.

PROJECT PLAN:
{final_plan}

Respond ONLY with JSON list:
[{{"summary": "...", "description": "..."}}]
""",
            expected_output="A JSON list of implementation tasks"
        )

        crew = Crew(agents=[development_task_extractor], tasks=[task], process="sequential", verbose=True)
        output = crew.kickoff()
        raw_output = output.raw

        json_start = raw_output.find("[")
        json_end = raw_output.rfind("]") + 1
        dev_tasks = json.loads(raw_output[json_start:json_end])

        return {"suggested_tasks": dev_tasks}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-code-snippet")
async def generate_code_snippet(data: CodeSnippetSingleTaskRequest):
    try:
        prompt = f"""
You are an experienced senior software engineer. Based on the project plan below, generate a code snippet.

### PROJECT PLAN
{data.final_plan}

### TASK
{data.task_name}
{data.task_description}

Return ONLY JSON:
{{"task": "Task name", "language": "Python | JS | etc.", "snippet": "your code"}}
"""
        response = client.chat.completions.create(
            model="o3",
            messages=[
                {"role": "system", "content": "You are a precise full-stack developer."},
                {"role": "user", "content": prompt}
            ]
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

        prompt = f"""
Given this plan, extract the tech stack across: Frontend, Backend, Database, Cloud, DevOps, Design.
Respond ONLY JSON:
[{{"name": "Frontend", "tech": ["React"]}}, ...]
PROJECT PLAN:
{final_plan}
"""
        response = client.chat.completions.create(
            model="o3",
            messages=[{"role": "system", "content": "You extract tech stack."}, {"role": "user", "content": prompt}]
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
            raise HTTPException(status_code=400, detail=f"No agent found for '{category}'")

        description = f"""
Given this project plan, list 5-10 dev tasks for {category}.
Respond ONLY JSON: [{{"summary": "...", "description": "..."}}]
PROJECT PLAN:
{final_plan}
"""
        task = Task(agent=agent, description=description, expected_output="JSON list of dev tasks")
        crew = Crew(agents=[agent], tasks=[task], process="sequential", verbose=True)
        output = crew.kickoff()

        raw = output.raw
        json_start = raw.find("[")
        json_end = raw.rfind("]") + 1
        return {"tasks": json.loads(raw[json_start:json_end])}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
