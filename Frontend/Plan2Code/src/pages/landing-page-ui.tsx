import { useState, useEffect } from "react";
import { GraduationCap } from "lucide-react";
import "./landing-page.scss";
import Chip from "@mui/material/Chip";
import Stack from "@mui/material/Stack";

const LandingPage = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [currentFeature, setCurrentFeature] = useState(0);

  useEffect(() => {
    setIsVisible(true);
    const interval = setInterval(() => {
      setCurrentFeature((prev) => (prev + 1) % 3);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <main>
      <div className="main-landing-page">
        <div className="container">
          <section className="cls-application-main">
            <Stack direction="column" spacing={1} className="cls-project-stack">
              <Chip
                label="Master Thesis Research Project - SRH Heidelberg"
                variant="outlined"
                icon={<GraduationCap className="icon" />}
                className="cls-chip"
                sx={{
                  padding: "22px",
                  color: "#ffffff",
                  backgroundColor: "transparent",
                  borderColor: "#ffffff",
                  width: "50%",
                  justifyContent: "center",
                  alignItems: "center",
                  textAlign: "center",
                }}
              />
              <h1>From Planning to Code Automated</h1>
              <p>
                Exploring AI-powered software development automation through
                reasoning models and agentic tools integration
              </p>
              <div className="cls-action-buttons">
                <a href="/demo" className="card card-secondary">
                  <div className="card-icon">
                    <span className="arrow">→</span>
                  </div>
                  <h3 className="card-title">Use the Application Form</h3>
                  <p className="card-subtitle">
                    Experience our platform firsthand
                  </p>
                </a>

                <a href="/file-upload" className="card card-secondary">
                  <div className="card-icon">
                    <svg
                      className="icon"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                    >
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                      <polyline points="14,2 14,8 20,8" />
                      <line x1="16" y1="13" x2="8" y2="13" />
                      <line x1="16" y1="17" x2="8" y2="17" />
                      <polyline points="10,9 9,9 8,9" />
                    </svg>
                  </div>
                  <h3 className="card-title">Upload requirements file</h3>
                  <p className="card-subtitle">
                    Upload a file you already have
                  </p>
                </a>
              </div>
              <div className="cls-card-container">
                <div className="card">
                  <h2 className="card-title">Sushant Huilgol</h2>
                  <p className="card-subtitle">Researcher & Developer</p>
                </div>

                <div className="card">
                  <h2 className="card-title">SRH Heidelberg</h2>
                  <p className="card-subtitle">Master Thesis 2025</p>
                </div>

                <div className="card">
                  <h2 className="card-title">AI Research</h2>
                  <p className="card-subtitle">Software Development</p>
                </div>
              </div>
            </Stack>
          </section>
        </div>
      </div>
    </main>
  );
};

export default LandingPage;
