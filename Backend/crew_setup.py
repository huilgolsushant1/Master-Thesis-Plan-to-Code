# crew_setup.py
from crewai import Task, Crew
from agents import (
    # Existing agents
    project_intake_analyst,
    business_objectives_mapper,
    risk_identifier,
    architecture_recommender,
    timeline_estimator,
    trend_research_agent,
    ticket_generator_agent,

    # New agents for added depth
    effort_estimator_agent,
    dependency_mapper_agent,
    sprint_planner_agent,
    critic_agent,
)

def build_crew(input_data):
    if hasattr(input_data, "dict"):
        summary = str(input_data.dict())
    else:
        # Already a dict (from normalize_input)
        summary = str(input_data)

    # Ordered workflow: validation → objectives → risks → architecture →
    # estimation → dependencies → sprint planning → trends → critic → tickets
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
            agent=effort_estimator_agent,
            description=f"Estimate effort (developer-days or story points) for major deliverables in: {summary}",
            expected_output="Effort estimation for each major deliverable/task, with totals per phase"
        ),
        Task(
            agent=dependency_mapper_agent,
            description=f"Identify task dependencies and opportunities for parallel execution for: {summary}",
            expected_output="List of dependencies, parallel work streams, and identification of critical path"
        ),
        Task(
            agent=sprint_planner_agent,
            description=f"Distribute deliverables into realistic 2-week sprints for a 6-month roadmap for: {summary}",
            expected_output="12 sprints with allocated features, parallel execution where possible, and milestones"
        ),
        Task(
            agent=trend_research_agent,
            description=f"Suggest modern best practices and tooling updates for: {summary}",
            expected_output="A brief overview of current industry trends, modern tooling choices, and best practices for similar systems"
        ),
        Task(
            agent=critic_agent,
            description=f"Review the draft project plan for realism, gaps, and execution readiness based on: {summary}",
            expected_output="Critique and recommendations for improving the plan so it’s execution-ready"
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
            effort_estimator_agent,
            dependency_mapper_agent,
            sprint_planner_agent,
            trend_research_agent,
            critic_agent,
            ticket_generator_agent
        ],
        tasks=tasks,
        process="sequential",
        verbose=True
    )

    return crew
