def build_prompt_from_agents(agent_output):
    return f"""
You are a senior software architect and project planner. Based on the following multi-agent analysis, generate a **comprehensive and detailed planning document** for the software project described.

Your output must include the following sections, each with rich detail, bullet points, and structured formatting:

---

### 1. Executive Summary & Project Charter
- Project background and justification
- Vision, mission, and business case
- Stakeholder matrix and approval authority
- Scope boundaries (inclusions and exclusions)
- Success criteria and KPIs

### 2. Business Goals and Objectives
- Strategic business goals
- Technical and operational objectives
- User experience and accessibility goals

### 3. Work Breakdown Structure (WBS)
- Major deliverables and sub-deliverables
- WBS codes and task groupings
- Mapping to project phases

### 4. Risk Assessment and Mitigation
- Technical, resource, and integration risks
- Security and compliance risks
- Mitigation strategies and escalation paths

### 5. Architecture Recommendation
- System architecture pattern (e.g., microservices)
- Frontend, backend, database, and cloud design
- DevOps and CI/CD strategy
- Security architecture and data flow

### 6. Timeline and Sprint Plan
- 6-month roadmap with phases and milestones
- Sprint cadence and feature allocation
- Critical path and dependency mapping

### 7. Resource and Team Structure
- Role assignments for all major functions
- Team structure for 50-person onsite team
- Skillset alignment with tech stack

### 8. Budget Allocation
- Cost breakdown by phase and function
- Infrastructure, tooling, and contingency
- Budget tracking and control mechanisms

### 9. Quality and Governance Plan
- QA strategy, testing phases, and quality gates
- Change control and versioning policy
- Communication and escalation protocols

### 10. Best Practices and Modern Trends
- Industry-standard tooling and frameworks
- Accessibility, observability, and performance practices
- Cloud-native and DevOps recommendations

---

Use the following agent insights as your factual input:

{agent_output}

---

Do not explain what to do — instead, **perform the planning** as if you were a professional team delivering this document to stakeholders. Output must be 100% textual. No diagrams or tables.
"""