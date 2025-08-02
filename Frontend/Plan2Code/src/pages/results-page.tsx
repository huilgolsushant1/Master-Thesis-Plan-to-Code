import { useEffect, useState } from "react";
import {
  Container,
  Typography,
  Paper,
  CircularProgress,
  TextField,
  Button,
  Stack,
  Divider,
  Box,
  Card,
  CardContent,
  Modal,
} from "@mui/material";
import { Grid } from "@mui/material";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";
import "highlight.js/styles/github.css";
import { useLocation } from "react-router-dom";
import "./results-page.scss";
import { marked } from "marked";
import pdfMake from "pdfmake/build/pdfmake";
import pdfFonts from "pdfmake/build/vfs_fonts";

function ProjectPlanPage() {
  const [projectMarkdown, setProjectMarkdown] = useState("");
  const [loading, setLoading] = useState(true);
  const location = useLocation();
  let { formData } = location.state || {};
  const [feedback, setFeedback] = useState("");
  const [refining, setRefining] = useState(false);
  const [loadingSuggestedTickets, setLoadingSuggestedTickets] = useState(false);
  const [jiraResponse, setJiraResponse] = useState("");
  const [showSuggestedTicketsModal, setShowSuggestedTicketsModal] =
    useState(false);
  const [suggestedTickets, setSuggestedTickets] = useState<
    { summary: string; description: string }[]
  >([]);
  const [submittingAll, setSubmittingAll] = useState(false);
  pdfMake.vfs = pdfFonts.vfs;

  if (location.state.text) {
    formData = location.state;
  }

  if (!formData) {
    return <Typography>No data available</Typography>;
  }

  useEffect(() => {
    async function fetchProjectPlan() {
      try {
        let response: any;
        response = await fetch(
          "http://localhost:8000/api/generate-project-plan",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(formData),
          }
        );

        const data = await response.json();
        // response = {
        //   project_plan:
        //     "### 1. Executive Summary & Project Charter\n\n**Project Background and Justification**  \nThe NewERP project aims to develop a comprehensive Software as a Service (SaaS) Enterprise Resource Planning (ERP) solution that integrates various business functions, including finance, human resources, supply chain, and customer relations. The project is justified by the need for improved operational efficiency, real-time data insights, and streamlined processes across departments.\n\n**Vision, Mission, and Business Case**  \n- **Vision**: To empower organizations with a flexible and innovative ERP solution that adapts to their evolving needs.\n- **Mission**: To deliver a user-friendly, robust, and scalable ERP platform leveraging cutting-edge technology and AI capabilities.\n- **Business Case**: The NewERP solution is expected to enhance decision-making, reduce operational costs, and improve user engagement, ultimately leading to increased profitability.\n\n**Stakeholder Matrix and Approval Authority**  \n- **Stakeholders**: Project sponsors, department heads, end-users, IT team, compliance officers.\n- **Approval Authority**: Project Steering Committee consisting of senior management, responsible for major project decisions and resource allocation.\n\n**Scope Boundaries (Inclusions and Exclusions)**  \n- **Inclusions**: Development of core ERP modules (finance, HR, supply chain), AI integration, user training, compliance measures.\n- **Exclusions**: Customization for specific industry needs, third-party software integrations beyond initial scope.\n\n**Success Criteria and KPIs**  \n- Successful deployment on Azure within the timeline.\n- User adoption rates above 75% within three months post-launch.\n- Achievement of defined KPIs including system uptime, response times, and user satisfaction ratings.\n\n### 2. Business Goals and Objectives\n\n**Strategic Business Goals**  \n- Enhance operational efficiencies across departments.\n- Provide data-driven insights through integrated analytics.\n- Foster agility in business processes and decision-making.\n\n**Technical and Operational Objectives**  \n- Implement a scalable cloud architecture that supports multi-tenancy.\n- Ensure robust security and compliance with industry standards.\n- Establish a continuous delivery pipeline for regular updates and improvements.\n\n**User Experience and Accessibility Goals**  \n- Develop an intuitive user interface that adheres to accessibility standards.\n- Provide comprehensive onboarding and training resources for users.\n- Incorporate user feedback loops to enhance product usability.\n\n### 3. Work Breakdown Structure (WBS)\n\n**Major Deliverables and Sub-Deliverables**  \n1. Project Initiation  \n   - Kick-off meeting  \n   - Environment setup  \n   - Communication protocols  \n   \n2. Frontend Development  \n   - UI/UX design  \n   - Angular application setup  \n   - Foundational components development  \n\n3. Backend Development  \n   - ASP.NET Core project structure  \n   - RESTful API development  \n   - Database schema design (MongoDB)  \n\n4. Core Features Development  \n   - AI features for predictive analytics  \n   - API integrations for core modules  \n   - User authentication and access control  \n\n5. Testing and User Acceptance  \n   - Comprehensive functional testing  \n   - User acceptance testing sessions  \n   - Feedback adjustments  \n\n6. Deployment  \n   - Final deployment on Azure  \n   - User training sessions  \n   - Performance monitoring post-launch  \n\n**WBS Codes and Task Groupings**  \n- 1.0 Project Initiation  \n- 2.0 Frontend Development  \n- 3.0 Backend Development  \n- 4.0 Core Features Development  \n- 5.0 Testing and User Acceptance  \n- 6.0 Deployment  \n\n**Mapping to Project Phases**  \n- Phase 1: Project Initiation  \n- Phase 2: Development (Frontend and Backend)  \n- Phase 3: Feature Development  \n- Phase 4: Testing  \n- Phase 5: Deployment  \n\n### 4. Risk Assessment and Mitigation\n\n**Technical, Resource, and Integration Risks**  \n- Risk: Compatibility issues with Angular and .NET technologies.  \n  Mitigation: Conduct thorough technology assessments and proof of concepts early in the project.\n\n- Risk: Resource availability and expertise gaps.  \n  Mitigation: Invest in training programs and consider hiring specialists as needed.\n\n**Security and Compliance Risks**  \n- Risk: Non-compliance with GDPR and CCPA regulations.  \n  Mitigation: Embed compliance measures from project inception, including regular audits and data encryption practices.\n\n**Mitigation Strategies and Escalation Paths**  \n- Establish a risk management team to monitor and respond to identified risks regularly.\n- Implement a change management strategy to minimize disruptions during transitions.\n\n### 5. Architecture Recommendation\n\n**System Architecture Pattern**  \n- Microservices architecture to enable independent deployment and scalability of components.\n\n**Frontend, Backend, Database, and Cloud Design**  \n- Frontend: Angular for responsive UI development with state management.\n- Backend: ASP.NET Core for RESTful services, MongoDB for NoSQL database.\n- Cloud: Azure for hosting with a focus on scalability and security.\n\n**DevOps and CI/CD Strategy**  \n- Implement CI/CD pipelines using Azure DevOps for automated testing and deployment.\n- Use containerization (Docker) for environment consistency and scalability.\n\n**Security Architecture and Data Flow**  \n- Implement role-based access control (RBAC) for secure user management.\n- Ensure data encryption in transit and at rest, with compliance measures integrated from the outset.\n\n### 6. Timeline and Sprint Plan\n\n**6-Month Roadmap with Phases and Milestones**  \n- Month 1: Project kick-off and environment setup.\n- Month 2: Frontend architecture finalized and initial development.\n- Month 3: Backend development and initial API integrations.\n- Month 4: Core features development and AI integration.\n- Month 5: Comprehensive testing and UAT.\n- Month 6: Deployment and go-live.\n\n**Sprint Cadence and Feature Allocation**  \n- Bi-weekly sprints with sprint reviews and retrospectives.\n- Initial sprints focused on foundational components and API development.\n\n**Critical Path and Dependency Mapping**  \n- Frontend and backend development are interdependent; both must progress concurrently for API integration.\n\n### 7. Resource and Team Structure\n\n**Role Assignments for All Major Functions**  \n- Project Manager: Overall project coordination.\n- Frontend Developers: Responsible for UI/UX and application development.\n- Backend Developers: Tasked with API development and database integration.\n- QA Engineers: Focused on testing and quality assurance.\n- DevOps Engineers: Manage infrastructure and CI/CD pipelines.\n- Compliance Officers: Ensure adherence to regulations.\n\n**Team Structure for 50-Person Onsite Team**  \n- 10 Project Managers and Business Analysts  \n- 20 Frontend and Backend Developers  \n- 10 QA Engineers  \n- 5 DevOps Engineers  \n- 5 Compliance and Security Specialists  \n\n**Skillset Alignment with Tech Stack**  \n- Proficiency in Angular, ASP.NET Core, MongoDB, and Azure.\n- Experience in AI and machine learning for predictive analytics.\n\n### 8. Budget Allocation\n\n**Cost Breakdown by Phase and Function**  \n- Phase 1: Project initiation - 10% of total budget.\n- Phase 2: Development - 50% of total budget.\n- Phase 3: Testing - 20% of total budget.\n- Phase 4: Deployment - 20% of total budget.\n\n**Infrastructure, Tooling, and Contingency**  \n- Cloud infrastructure costs (Azure hosting, database services).\n- Development tools and licenses (Adobe XD, project management tools).\n- 10% contingency fund for unforeseen expenses.\n\n**Budget Tracking and Control Mechanisms**  \n- Monthly budget reviews against milestones.\n- Use of project management tools for real-time tracking.\n\n### 9. Quality and Governance Plan\n\n**QA Strategy, Testing Phases, and Quality Gates**  \n- Establish a multi-tiered testing strategy, including unit, integration, and user acceptance testing.\n- Define quality gates at each project phase to ensure adherence to specifications.\n\n**Change Control and Versioning Policy**  \n- Implement a change control board to evaluate and approve changes.\n- Versioning policy to maintain stability and track changes in codebase.\n\n**Communication and Escalation Protocols**  \n- Regular project status meetings with stakeholders.\n- Defined escalation paths for unresolved issues to senior management.\n\n### 10. Best Practices and Modern Trends\n\n**Industry-Standard Tooling and Frameworks**  \n- Use of Agile methodologies and tools (JIRA, Trello).\n- Adoption of cloud-native technologies and architecture.\n\n**Accessibility, Observability, and Performance Practices**  \n- Compliance with WCAG 2.1 for accessibility.\n- Implement observability tools (e.g., Azure Monitor) for performance tracking.\n\n**Cloud-Native and DevOps Recommendations**  \n- Emphasize container orchestration using Kubernetes for microservices management.\n- Continuous improvement practices to adapt to changing user needs and technologies.",
        // };
        // const data = response;
        setProjectMarkdown(data.project_plan);
      } catch (error) {
        console.error("Error fetching project plan:", error);
        setProjectMarkdown("# Error\nUnable to load project plan.");
      } finally {
        setLoading(false);
      }
    }

    fetchProjectPlan();
  }, []);

  async function handleRefine() {
    if (!projectMarkdown || !feedback.trim()) return;
    setRefining(true);
    try {
      const response = await fetch(
        "http://localhost:8000/api/refine-project-plan",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            original_plan: projectMarkdown,
            user_feedback: feedback,
          }),
        }
      );
      const result = await response.json();
      setProjectMarkdown(result.refined_plan);
      setFeedback("");
    } catch (error) {
      console.error("Refinement failed:", error);
    } finally {
      setRefining(false);
    }
  }

  async function handleGenerateTicketsFromPlan() {
    setLoadingSuggestedTickets(true);
    setShowSuggestedTicketsModal(true);
    try {
      const response = await fetch(
        "http://localhost:8000/api/generate-jira-tickets-from-plan",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ plan: projectMarkdown }),
        }
      );
      const data = await response.json();
      setSuggestedTickets(data.tickets || []);
    } catch (error) {
      console.error("Ticket suggestion error:", error);
    } finally {
      setLoadingSuggestedTickets(false); // Hide loader
    }
  }

  async function handleSubmitAllTickets() {
    setSubmittingAll(true);
    try {
      const response = await fetch(
        "http://localhost:8000/api/push-finalized-tickets",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(suggestedTickets),
        }
      );
      const data = await response.json();
      const results = (data.created || []).map((res: any) =>
        res.key ? `✅ ${res.key} — [View](${res.url})` : `${res.error}`
      );
      setJiraResponse(results.join("\n"));
      setShowSuggestedTicketsModal(false);
    } catch (error) {
      console.error("Bulk submission error:", error);
      setJiraResponse("Error submitting tickets.");
    } finally {
      setSubmittingAll(false);
    }
  }

  const handleDownloadStyledPdf = () => {
    const htmlResult = marked.parse(projectMarkdown);
    Promise.resolve(htmlResult).then((html) => {
      const container = document.createElement("div");
      container.innerHTML = html;

      const content: any[] = [];

      container.childNodes.forEach((node) => {
        if (node.nodeName === "H1") {
          content.push({ text: node.textContent, style: "header1" });
        } else if (node.nodeName === "H2") {
          content.push({ text: node.textContent, style: "header2" });
        } else if (node.nodeName === "H3") {
          content.push({ text: node.textContent, style: "header3" });
        } else if (node.nodeName === "P") {
          content.push({ text: node.textContent, style: "paragraph" });
        } else if (node.nodeName === "PRE") {
          content.push({
            text: node.textContent,
            style: "codeBlock",
            font: "Courier",
          });
        } else if (node.nodeName === "UL") {
          const items = Array.from(
            (node as Element).querySelectorAll("li")
          ).map((li) => ({
            text: li.textContent,
          }));
          content.push({ ul: items, style: "list" });
        }
      });

      const docDefinition = {
        content,
        styles: {
          header1: {
            fontSize: 20,
            bold: true,
            margin: [0, 20, 0, 10] as [number, number, number, number],
          },
          header2: {
            fontSize: 16,
            bold: true,
            margin: [0, 18, 0, 8] as [number, number, number, number],
          },
          header3: {
            fontSize: 14,
            bold: true,
            margin: [0, 16, 0, 6] as [number, number, number, number],
          },
          paragraph: {
            fontSize: 11,
            lineHeight: 1.7,
            margin: [0, 4, 0, 4] as [number, number, number, number],
          },
          list: {
            fontSize: 11,
            margin: [10, 4, 0, 4] as [number, number, number, number],
          },
          codeBlock: {
            background: "#f6f8fa",
            fontSize: 10,
            margin: [0, 10, 0, 10] as [number, number, number, number],
            color: "#333",
          },
        },
        defaultStyle: {
          fontSize: 11,
        },
      };

      pdfMake.createPdf(docDefinition).download("project-plan.pdf");
    });
  };

  return (
    <Container maxWidth="md" className="project-plan-container">
      {loading || refining ? (
        <CircularProgress />
      ) : (
        <Paper elevation={6} className="markdown-paper">
          <ReactMarkdown
            children={projectMarkdown}
            remarkPlugins={[remarkGfm]}
            rehypePlugins={[rehypeHighlight]}
            components={{
              h1: ({ node, ref, ...props }) => (
                <h1 id={slugify(props.children)} {...props} />
              ),
              h2: ({ node, ref, ...props }) => (
                <h2 id={slugify(props.children)} {...props} />
              ),
              h3: ({ node, ref, ...props }) => (
                <h3 id={slugify(props.children)} {...props} />
              ),
            }}
          />
        </Paper>
      )}
      <Divider sx={{ my: 4 }} />

      <Stack spacing={2}>
        <Typography variant="h6">Refine this Plan</Typography>

        <TextField
          label="Your Feedback"
          placeholder="e.g. Make the architecture serverless using AWS Lambda"
          value={feedback}
          onChange={(e) => setFeedback(e.target.value)}
          multiline
          minRows={3}
          fullWidth
          variant="outlined"
        />

        <Button
          variant="contained"
          color="primary"
          onClick={handleRefine}
          disabled={refining || !feedback.trim()}
        >
          {refining ? "Refining..." : "Apply Refinement"}
        </Button>
      </Stack>

      <Divider sx={{ my: 4 }} />
      <div className="action-buttons">
        <Button
          variant="outlined"
          color="primary"
          onClick={handleDownloadStyledPdf}
          sx={{ mt: 2 }}
        >
          Download Styled PDF
        </Button>

        <Button
          variant="outlined"
          onClick={handleGenerateTicketsFromPlan}
          sx={{ mt: 2 }}
        >
          Generate Suggested JIRA Tickets
        </Button>
      </div>

      <Modal
        open={showSuggestedTicketsModal}
        onClose={() => setShowSuggestedTicketsModal(false)}
      >
        <Box
          sx={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            width: "90%",
            bgcolor: "background.paper",
            boxShadow: 24,
            p: 4,
            borderRadius: 2,
            maxHeight: "90vh",
            overflow: "auto",
          }}
        >
          <Typography variant="h6" gutterBottom>
            Suggested Tickets
          </Typography>

          {loadingSuggestedTickets ? (
            <Box sx={{ display: "flex", justifyContent: "center", my: 4 }}>
              <CircularProgress />
            </Box>
          ) : (
            <>
              <Grid container className="ticket-grid">
                {suggestedTickets.map((ticket, index) => (
                  <div key={index} className="ticket-card-wrapper">
                    <Card className="ticket-card">
                      <CardContent>
                        <TextField
                          label="Summary"
                          fullWidth
                          value={ticket.summary}
                          onChange={(e) => {
                            const updated = [...suggestedTickets];
                            updated[index].summary = e.target.value;
                            setSuggestedTickets(updated);
                          }}
                          sx={{ mb: 1 }}
                        />
                        <TextField
                          label="Description"
                          fullWidth
                          multiline
                          minRows={3}
                          value={ticket.description}
                          onChange={(e) => {
                            const updated = [...suggestedTickets];
                            updated[index].description = e.target.value;
                            setSuggestedTickets(updated);
                          }}
                        />
                      </CardContent>
                    </Card>
                  </div>
                ))}
              </Grid>

              <Button
                variant="contained"
                color="success"
                onClick={handleSubmitAllTickets}
                disabled={submittingAll}
                sx={{ mt: 3 }}
              >
                {submittingAll ? "Submitting..." : "Submit All to JIRA"}
              </Button>
            </>
          )}
        </Box>
      </Modal>
    </Container>
  );
}

function slugify(children: React.ReactNode): string {
  const text = Array.isArray(children)
    ? children.join("")
    : typeof children === "string"
    ? children
    : String(children);
  return text
    .toLowerCase()
    .replace(/\s+/g, "-")
    .replace(/[^\w-]/g, "");
}

export default ProjectPlanPage;
