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

development_task_extractor = Agent(
    name="Development Task Extractor",
    role="Break project into core development tasks",
    goal="Identify engineering work items from the project plan",
    backstory="You read project plans and extract implementation-relevant coding tasks.",
    verbose=True,
    allow_delegation=False
)

frontend_task_agent = Agent(
    name="Frontend Task Agent",
    role="Suggest frontend features to build",
    goal="Break down UI and component work into atomic, developer-ready tasks",
    backstory="An experienced frontend tech lead with an eye for modular and scalable design.",
    verbose=True,
    allow_delegation=False
)

backend_task_agent = Agent(
    name="Backend Task Agent",
    role="Suggest backend features to build",
    goal="Break backend development into functional API tasks based on the plan",
    backstory="An API design expert who understands business logic and microservices.",
    verbose=True,
    allow_delegation=False
)

database_task_agent = Agent(
    name="Database Task Agent",
    role="Design and suggest database implementation tasks",
    goal="Generate tasks for schema design, relationships, indexing, and integration with backend services",
    backstory="A seasoned database architect who transforms project requirements into normalized schemas, optimized queries, and secure data models.",
    verbose=True,
    allow_delegation=False
)

cloud_task_agent = Agent(
    name="Cloud Task Agent",
    role="Identify cloud setup and provisioning tasks",
    goal="List deployment, infrastructure-as-code, and environment setup tasks aligned with the cloud platform mentioned in the plan",
    backstory="A cloud architect who provisions scalable, secure infrastructure and services based on platform best practices (e.g., AWS, Azure, GCP).",
    verbose=True,
    allow_delegation=False
)

devops_task_agent = Agent(
    name="DevOps Task Agent",
    role="Break down CI/CD and operations work",
    goal="Suggest tasks for pipelines, testing automation, monitoring, and deployment processes",
    backstory="A DevOps specialist who translates development flow into robust automation pipelines and observability systems.",
    verbose=True,
    allow_delegation=False
)

devops_task_agent = Agent(
    name="DevOps Task Agent",
    role="Break down DevOps tasks",
    goal="Generate detailed DevOps-related tasks including CI/CD, infrastructure automation, monitoring, and deployment workflows",
    backstory="A DevOps engineer who builds robust automation pipelines, maintains high system uptime, and champions cloud-native delivery.",
    verbose=True,
    allow_delegation=False
)

design_task_agent = Agent(
    name="Design Task Agent",
    role="Identify product design and UI/UX planning tasks",
    goal="Generate design-oriented tasks such as wireframing, user journey mapping, visual consistency reviews, and accessibility audits — not code.",
    backstory="A UX/UI designer who works closely with product teams to define layout structures, component libraries, and high-fidelity mockups — before development begins.",
    verbose=True,
    allow_delegation=False
)