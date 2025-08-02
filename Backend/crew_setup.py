from crewai import Task, Crew
from agents import (
    project_intake_analyst,
    business_objectives_mapper,
    risk_identifier,
    architecture_recommender,
    timeline_estimator,
    trend_research_agent,
    ticket_generator_agent
)

def build_crew(input_data):
    summary = str(input_data.dict())

    tasks = [
        Task(
            agent=project_intake_analyst,
            description=f"Refine and validate this project input: {summary}",
            expected_output="A well-structured summary of validated and completed input fields"
        ),
        Task(
            agent=business_objectives_mapper,
            description=f"Extract goals and KPIs from: {summary}",
            expected_output="A list of business goals and measurable KPIs for this project"
        ),
        Task(
            agent=risk_identifier,
            description=f"Analyze risks for: {summary}",
            expected_output="A list of risks with brief mitigation strategies relevant to the project’s tech, team, and scope"
        ),
        Task(
            agent=architecture_recommender,
            description=f"Recommend a system architecture for: {summary}",
            expected_output="A detailed architecture plan based on the provided tech stack, budget, and team size"
        ),
        Task(
            agent=timeline_estimator,
            description=f"Create a 6-month sprint roadmap for: {summary}",
            expected_output="A sprint-based roadmap with timelines, milestones, and phase descriptions"
        ),
        Task(
            agent=trend_research_agent,
            description=f"Suggest modern best practices and tooling updates for: {summary}",
            expected_output="A brief overview of current industry trends, modern tooling choices, and best practices for similar systems"
        ),
        Task(
            agent=ticket_generator_agent,
            description="Extract actionable tasks from the project plan and suggest them as JIRA ticket summaries and descriptions",
            expected_output='A JSON list of {"summary": ..., "description": ...} for each suggested ticket, derived from key project plan sections'
        )
    ]

    crew = Crew(
    agents=[
        project_intake_analyst,
        business_objectives_mapper,
        risk_identifier,
        architecture_recommender,
        timeline_estimator,
        trend_research_agent,
        ticket_generator_agent
    ],
    tasks=tasks,
    process="sequential",
    verbose=True
)


    return crew