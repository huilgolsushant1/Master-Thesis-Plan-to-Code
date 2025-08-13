import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import LandingPage from "../pages/landing-page-ui";
import ProjectPlanningUI from "../pages/project-planning-ui";
import ProjectPlanPage from "../pages/results-page";
import TextFileUpload from "../pages/file-upload-ui";
import PushedTicketsPage from "../pages/development-tasks-page";

const AppRoutes: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/demo" element={<ProjectPlanningUI />} />
        <Route path="/results" element={<ProjectPlanPage />} />
        <Route path="/file-upload" element={<TextFileUpload />} />
        <Route path="/development-tasks" element={<PushedTicketsPage />} />
      </Routes>
    </Router>
  );
};

export default AppRoutes;
