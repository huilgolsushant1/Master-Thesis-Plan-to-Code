def build_prompt_from_agents(agent_output: str) -> str:
    return f"""
You are a senior software architect and project planner. Based on the following multi-agent analysis, generate a **professional, execution-ready planning document** for the described project.

Your output must include **structured, detailed, and realistic execution-level planning**, with human-readable sections for the UI.
Make sure necessary texts are bolded or highlighted for clarity.
--- Human-readable sections to include ---

# Include the title of the Project Plan at the top of the document. It should be highlighted as a title.

### 1. Executive Summary & Project Charter
- Background and justification
- Vision, mission, and business case
- Stakeholder matrix and approval authority
- Scope boundaries (inclusions and exclusions)
- Success criteria and KPIs
- This is a critical section, do not be generic
- Keep the content in detail, do not be generic

### 2. Business Goals and Objectives
- Strategic business goals
- Technical and operational objectives
- UX and accessibility goals
- Compliance and security objectives
- Highlight key goals and objectives
- Keep the content in detail, do not be generic

### 3. Work Breakdown Structure (WBS) with Effort Estimation
- Major deliverables and sub-deliverables
- WBS codes and task groupings
- **Effort estimation for each task (in working-days or story points)**
- Role assignment (who is expected to work on it)
- Include a WBS Table with tasks, WBS codes, effort estimates, and role assignments
- Highlight high-effort tasks and potential resource constraints

### 4. Task Dependencies
- Explicit mapping of dependencies (which tasks must finish before others start)
- Tasks that can run in parallel across teams
- Critical path identification
- Highlight critical dependencies and potential bottlenecks
- Keep the content in detail, do not be generic
- Include Tables if needed
- This is a critical section, do not be generic
- Make sure to give a detailed task dependency mapping with realistic dependencies and parallel tasks.
- The critical path should be clearly identified and explained. Depict it in a nice way which is easy to understand.

### 5. Risk Assessment and Mitigation
- Technical, resource, and integration risks
- Security and compliance risks
- Mitigation strategies
- Contingency plans
- Risk monitoring approach
- Highlight high-impact/high-probability risks
- Suggest risk mitigation strategies
- Keep the content in detail, do not be generic

### 6. Architecture Recommendation
- System architecture pattern (e.g. microservices)
- Frontend, backend, database, cloud design, UI/UX
- DevOps and CI/CD strategy
- Security and data flow
- Make sure to give only 1 recommendation, not multiple options
- Justify why this is the best fit for the project
- This should be represented in a bullet-point format, do not be generic

### 7. Timeline and Sprint Plan
- Realistic sprint plan (2-week sprints)
- For 6 months → ~12 sprints, mapped with features/deliverables
- Parallel execution shown (e.g., backend + frontend teams working simultaneously)
- Milestones and critical dependencies
- High-level timeline & Milestones Table
- Highlight if timeline is too aggressive for scope/team size
- This is a critical section, do not be generic. Make sure to give a detailed timeline with realistic milestones. Table is mandatory.

### 8. Resource & Team Structure
- Detailed role assignments (frontend devs, backend devs, data engineers, QA, DevOps, architects, etc.)
- Mapping of effort to team capacity
- Highlight if current team size is under/over capacity for timeline

### 9. Budget & Cost Breakdown
- Estimate the total budget. Calculate it based on the project's team size, roles, and timeline.
- Provide a detailed cost breakdown table with the following columns: Category, Calculation Basis, Estimated Cost, and Notes.
- Calculate Labor Costs: Use the formula: (Number of people in a role) × (Number of working days) × (Average fully-loaded day rate for that role). Define the average day rates used in your calculation (e.g., Developer: €600/day, Project Manager: €800/day).
- Itemize Non-Labor Costs: Separately list and estimate infrastructure (cloud hosting, SaaS tools), third-party services/licensing, and a contingency buffer.
- Justify the Contingency Buffer: Set the contingency to 10-20% of the total budget and explicitly link this to the high-risk items identified in the Risk Assessment section (e.g., "15% contingency due to AI integration complexity").
- Budget Tracking: Recommend a specific method for tracking (e.g., "Monthly budget vs. actuals review using a dedicated dashboard").
- Adequacy Analysis: Explicitly state: "Based on this calculation, the estimated budget is [Sufficient/Insufficient] for the defined scope and timeline."
- If Insufficient, Recommend Specific Actions: Provide concrete options, for example:
- Descope: "Delay the implementation of [Specific Feature] to a Phase 2."
- Extend Timeline: "A 2-month extension would reduce monthly burn rate by X%."
- Adjust Resources: "Reduce the frontend team by one developer and extend the timeline for frontend tasks."
- Mention that the budget is an estimate and actual costs may vary based on real-world factors.

### 10. Quality and Governance
- QA strategy (unit tests, integration tests, UAT)
- Governance, communication & escalation protocols
- Agile ceremonies (standups, retrospectives)
- Change management process
- Highlight critical quality risks and mitigation strategies
- Keep the content in detail, do not be generic
- This should be represented in a bullet-point format, do not be generic

### 11. Best Practices and Modern Trends
- Observability, performance optimization
- Cloud-native practices
- DevOps & CI/CD maturity model alignment
- Security best practices (OWASP Top 10, data protection)
- Accessibility standards (WCAG compliance)
- Highlight cutting-edge practices relevant to the project
- Justify why these practices are important for the project's success
- This should be represented in a bullet-point format, do not be generic

--- End of human-readable requirements ---

Do not include any sections beyond those listed above. Ensure the document is well-structured, detailed, and tailored to the specific project described in the analysis.
{agent_output}
"""
