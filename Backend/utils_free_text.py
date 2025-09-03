import json
import os
from openai import OpenAI
from crew_setup import build_crew
from pydantic import BaseModel
from typing import List, Optional

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

# ------------------ FREE TEXT EXTRACTION ------------------

def call_llm_to_extract_json_from_free_text(free_text: str) -> str:
    """
    Call OpenAI to parse free-text brief into structured JSON fields.
    Returns raw string (may include JSON or markdown formatting).
    """
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
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a precise project planner."},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )
    return response.choices[0].message.content.strip()


def try_extract_hidden_plan_json(raw_output: str) -> dict:
    """
    Attempt to extract JSON from raw LLM output.
    Handles fenced code blocks or extra formatting.
    """
    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        cleaned = raw_output.strip("```json").strip("```").strip()
        try:
            return json.loads(cleaned)
        except Exception:
            return None


# ------------------ NORMALIZATION ------------------

def normalize_input(input_payload):
    """
    Accept either:
    - ProjectInput (structured)
    - dict (structured JSON)
    - str (free-text brief)

    Returns canonical dict 'agent_input' for agents.
    """
    if isinstance(input_payload, ProjectInput):
        return {
            "projectName": input_payload.projectName,
            "projectDescription": input_payload.projectDescription,
            "stakeholders": input_payload.stakeholder,
            "techStack": {
                "frontend": input_payload.frontend,
                "backend": input_payload.backend,
                "database": input_payload.database,
                "cloud": input_payload.cloud,
                "devops": input_payload.devops,
                "design": input_payload.design
            },
            "meta": {
                "startDate": input_payload.startDate,
                "duration": input_payload.expectedDuration,
                "teamSize": input_payload.teamSize,
                "budget": input_payload.budget,
                "experience": input_payload.experience,
                "locationType": input_payload.locationType,
                "otherTech": input_payload.otherTech
            }
        }

    elif isinstance(input_payload, str):
        # Free-text brief
        raw_output = call_llm_to_extract_json_from_free_text(input_payload)
        brief_json = try_extract_hidden_plan_json(raw_output)
        if brief_json:
            return {
                "projectName": brief_json.get("projectName", ""),
                "projectDescription": brief_json.get("projectDescription", ""),
                "stakeholders": brief_json.get("stakeholder", ""),
                "techStack": {
                    "frontend": brief_json.get("frontend", []),
                    "backend": brief_json.get("backend", []),
                    "database": brief_json.get("database", []),
                    "cloud": brief_json.get("cloud", []),
                    "devops": brief_json.get("devops", []),
                    "design": brief_json.get("design", [])
                },
                "meta": {
                    "startDate": brief_json.get("startDate", ""),
                    "duration": brief_json.get("expectedDuration", ""),
                    "teamSize": brief_json.get("teamSize", ""),
                    "budget": brief_json.get("budget", ""),
                    "experience": brief_json.get("experience", ""),
                    "locationType": brief_json.get("locationType", ""),
                    "otherTech": brief_json.get("otherTech", "")
                }
            }
        else:
            return {
                "projectName": "",
                "projectDescription": input_payload,
                "stakeholders": "",
                "techStack": {},
                "meta": {}
            }

    elif isinstance(input_payload, dict):
        # Handle dict directly (already structured JSON)
        try:
            pi = ProjectInput(**input_payload)
            return normalize_input(pi)
        except Exception:
            return {"projectDescription": str(input_payload)}

    else:
        return {"projectDescription": str(input_payload)}


# ------------------ AGENT RUNNER ------------------

def run_agents_wrapper(agent_input: dict):
    """
    Wrapper that builds a Crew and kicks it off using normalized input.
    """
    crew = build_crew(agent_input)
    return crew.kickoff()
