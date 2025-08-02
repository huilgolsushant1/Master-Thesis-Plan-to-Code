from crewai import Agent
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")

project_intake_analyst = Agent(
    name="Project Intake Analyst",
    role="Validate and enrich project input",
    goal="Ensure clarity and completeness",
    backstory="An analyst who preps project briefs for AI systems.",
    llm=llm
)

business_objectives_mapper = Agent(
    name="Business Objectives Mapper",
    role="Map business goals",
    goal="Align project goals with business KPIs",
    backstory="A strategist for stakeholder objectives.",
    llm=llm
)

risk_identifier = Agent(
    name="Risk Identifier",
    role="Flag project risks",
    goal="Highlight and mitigate risks early",
    backstory="A risk consultant for enterprise systems.",
    llm=llm
)

architecture_recommender = Agent(
    name="Architecture Recommender",
    role="Suggest optimal architecture",
    goal="Design modern, scalable systems",
    backstory="A tech lead who designs clean backends.",
    llm=llm
)

timeline_estimator = Agent(
    name="Timeline Estimator",
    role="Break project into sprints",
    goal="Create a 6-month agile roadmap",
    backstory="A PM who knows when things break down.",
    llm=llm
)

trend_research_agent = Agent(
    name="Trend Research Agent",
    role="Inject modern best practices",
    goal="Ensure architecture and dev stack are future-proof",
    backstory="A thought leader who studies dev conferences and cloud blogs.",
    llm=llm
)

ticket_generator_agent = Agent(
    name="Ticket Generator Agent",
    role="Ticket Generation Specialist",
    goal="Break down the project plan into actionable, JIRA-friendly tasks",
    backstory="You are a precise and methodical planner with experience in Agile delivery. Your job is to translate structured plans into JIRA-ready ticket summaries and descriptions.",
    verbose=True,
    allow_delegation=False,
)