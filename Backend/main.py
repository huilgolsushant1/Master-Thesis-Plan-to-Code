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
from agents import ticket_generator_agent
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
            # Wrap the plain description text in Atlassian Document Format (ADF)
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
                results.append(
                    {
                        "summary": ticket.summary,
                        "key": issue["key"],
                        "url": f"{os.getenv('JIRA_BASE_URL')}/browse/{issue['key']}",
                    }
                )
            else:
                results.append({"summary": ticket.summary, "error": response.text})

        return {"created_issues": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
