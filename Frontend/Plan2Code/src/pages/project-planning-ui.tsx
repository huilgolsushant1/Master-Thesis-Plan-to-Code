import React, { useState } from "react";
import {
  Stepper,
  Step,
  StepLabel,
  Button,
  Typography,
  TextField,
  MenuItem,
  Checkbox,
  FormControlLabel,
  FormGroup,
  Card,
  CardContent,
  Divider,
  Box,
  Snackbar,
  Alert,
} from "@mui/material";
import { Grid } from "@mui/material";
import "./project-planning.scss";
import { useNavigate } from "react-router-dom";

const steps = [
  "Project Overview",
  "Timeline & Resources",
  "Tech Stack",
  "Review & Generate",
];

const techCategories = [
  {
    label: "Frontend",
    field: "frontend",
    options: ["React", "Angular", "Vue.js"],
  },
  {
    label: "Backend",
    field: "backend",
    options: ["Node.js", "C#/.NET", "Go"],
  },
  {
    label: "Database",
    field: "database",
    options: ["SQL", "MongoDB", "Firebase"],
  },
  {
    label: "Cloud",
    field: "cloud",
    options: ["AWS", "Azure", "Google Cloud"],
  },
  {
    label: "DevOps",
    field: "devops",
    options: ["Docker", "Kubernetes", "Jenkins"],
  },
  {
    label: "Design Tools",
    field: "design",
    options: ["Figma", "Adobe XD"],
  },
];

interface FormData {
  projectName: string;
  projectDescription: string;
  stakeholder: string;
  category: string;
  startDate: string;
  expectedDuration: string;
  durationUnit: string;
  teamSize: string;
  budget: string;
  experience: string;
  locationType: string;
  frontend: string[];
  backend: string[];
  database: string[];
  cloud: string[];
  devops: string[];
  design: string[];
  otherTech: string | undefined;
}

interface Errors {
  [key: string]: string;
}

const StepperForm = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [formData, setFormData] = useState<FormData>({
    projectName: "",
    projectDescription: "",
    stakeholder: "",
    category: "",
    startDate: "",
    expectedDuration: "",
    durationUnit: "months",
    teamSize: "",
    budget: "",
    experience: "",
    locationType: "",
    frontend: [],
    backend: [],
    database: [],
    cloud: [],
    devops: [],
    design: [],
    otherTech: "",
  });
  const [errors, setErrors] = useState<Errors>({});
  const [submitted, setSubmitted] = useState(false);
  const navigate = useNavigate();

  const handleChange = (field: keyof FormData, value: string) => {
    setFormData((prev: FormData) => ({ ...prev, [field]: value }));
    setErrors((prev: Errors) => ({ ...prev, [field]: "" }));
  };

  const handleCheckboxChange = (
    field: keyof Pick<
      FormData,
      "frontend" | "backend" | "database" | "cloud" | "devops" | "design"
    >,
    option: string
  ) => {
    setFormData((prev) => {
      const current = prev[field] as string[];
      const updated = current.includes(option)
        ? current.filter((item) => item !== option)
        : [...current, option];
      return { ...prev, [field]: updated };
    });
  };

  const handleSubmit = () => {
    setSubmitted(true);
    navigate("/results", { state: { formData } });
  };

  const validateStep = () => {
    const newErrors: Errors = {};

    if (activeStep === 0) {
      if (!formData.projectName) newErrors.projectName = "Required";
      if (!formData.stakeholder) newErrors.stakeholder = "Required";
      if (!formData.category) newErrors.category = "Required";
      if (!formData.projectDescription)
        newErrors.projectDescription = "Required";
    }
    if (activeStep === 1) {
      if (!formData.startDate) newErrors.startDate = "Required";
      if (!formData.expectedDuration) newErrors.expectedDuration = "Required";
      if (!formData.teamSize) newErrors.teamSize = "Required";
      if (!formData.budget) newErrors.budget = "Required";
      if (!formData.experience) newErrors.experience = "Required";
      if (!formData.locationType) newErrors.locationType = "Required";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const renderStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <>
            <TextField
              fullWidth
              label="Project Name"
              margin="normal"
              value={formData.projectName}
              onChange={(e) => handleChange("projectName", e.target.value)}
              error={!!errors.projectName}
              helperText={errors.projectName}
            />
            <TextField
              fullWidth
              label="Client or Stakeholder Name"
              margin="normal"
              value={formData.stakeholder}
              onChange={(e) => handleChange("stakeholder", e.target.value)}
              error={!!errors.stakeholder}
              helperText={errors.stakeholder}
            />
            <TextField
              fullWidth
              select
              label="Project Category"
              margin="normal"
              value={formData.category}
              onChange={(e) => handleChange("category", e.target.value)}
              error={!!errors.category}
              helperText={errors.category}
            >
              {["Internal", "Client-facing", "R&D"].map((option) => (
                <MenuItem key={option} value={option}>
                  {option}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              fullWidth
              multiline
              rows={4}
              label="Project Description"
              margin="normal"
              value={formData.projectDescription}
              onChange={(e) =>
                handleChange("projectDescription", e.target.value)
              }
              error={!!errors.projectDescription}
              helperText={errors.projectDescription}
            />
          </>
        );
      case 1:
        return (
          <>
            <TextField
              fullWidth
              type="date"
              label="Start Date"
              margin="normal"
              InputLabelProps={{ shrink: true }}
              value={formData.startDate}
              onChange={(e) => handleChange("startDate", e.target.value)}
              error={!!errors.startDate}
              helperText={errors.startDate}
            />
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Expected Duration"
                  type="number"
                  margin="normal"
                  value={formData.expectedDuration}
                  onChange={(e) =>
                    handleChange("expectedDuration", e.target.value)
                  }
                  error={!!errors.expectedDuration}
                  helperText={errors.expectedDuration}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  select
                  label="Unit"
                  margin="normal"
                  value={formData.durationUnit}
                  onChange={(e) => handleChange("durationUnit", e.target.value)}
                >
                  {["days", "weeks", "months"].map((option) => (
                    <MenuItem key={option} value={option}>
                      {option}
                    </MenuItem>
                  ))}
                </TextField>
              </Grid>
            </Grid>
            <TextField
              fullWidth
              type="number"
              label="Team Size"
              margin="normal"
              value={formData.teamSize}
              onChange={(e) => handleChange("teamSize", e.target.value)}
              error={!!errors.teamSize}
              helperText={errors.teamSize}
            />
            <TextField
              fullWidth
              type="number"
              label="Budget in Euros"
              margin="normal"
              value={formData.budget}
              onChange={(e) => handleChange("budget", e.target.value)}
              error={!!errors.budget}
              helperText={errors.budget}
            />
            <TextField
              fullWidth
              select
              label="Team Experience"
              margin="normal"
              value={formData.experience}
              onChange={(e) => handleChange("experience", e.target.value)}
              error={!!errors.experience}
              helperText={errors.experience}
            >
              {["Beginner", "Intermediate", "Advanced"].map((level) => (
                <MenuItem key={level} value={level}>
                  {level}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              fullWidth
              select
              label="Team Location Type"
              margin="normal"
              value={formData.locationType}
              onChange={(e) => handleChange("locationType", e.target.value)}
              error={!!errors.locationType}
              helperText={errors.locationType}
            >
              {["Remote", "Onsite", "Hybrid"].map((type) => (
                <MenuItem key={type} value={type}>
                  {type}
                </MenuItem>
              ))}
            </TextField>
          </>
        );
      case 2:
        return (
          <>
            {techCategories.map(({ label, field, options }) => (
              <Box key={field} sx={{ mt: 2 }}>
                <Typography variant="h6">{label} Technologies</Typography>
                <FormGroup>
                  {options.map((tech) => (
                    <FormControlLabel
                      key={tech}
                      control={
                        <Checkbox
                          checked={(
                            formData[field as keyof FormData] as string[]
                          ).includes(tech)}
                          onChange={() =>
                            handleCheckboxChange(
                              field as
                                | "frontend"
                                | "backend"
                                | "database"
                                | "cloud"
                                | "devops"
                                | "design",
                              tech
                            )
                          }
                        />
                      }
                      label={tech}
                    />
                  ))}
                </FormGroup>
              </Box>
            ))}
            <TextField
              fullWidth
              multiline
              rows={3}
              label="Other Technologies"
              margin="normal"
              value={formData.otherTech}
              onChange={(e) => handleChange("otherTech", e.target.value)}
            />
          </>
        );
      case 3:
        return (
          <Card>
            <CardContent>
              <Typography variant="h6">Review Your Project</Typography>
              <Typography>
                <strong>Project Name:</strong> {formData.projectName}
              </Typography>
              <Typography>
                <strong>Stakeholder:</strong> {formData.stakeholder}
              </Typography>
              <Typography>
                <strong>Category:</strong> {formData.category}
              </Typography>
              <Typography>
                <strong>Description:</strong> {formData.projectDescription}
              </Typography>
              <Divider sx={{ my: 2 }} />
              <Typography>
                <strong>Start Date:</strong> {formData.startDate}
              </Typography>
              <Typography>
                <strong>Duration:</strong> {formData.expectedDuration}{" "}
                {formData.durationUnit}
              </Typography>
              <Typography>
                <strong>Team Size:</strong> {formData.teamSize}
              </Typography>
              <Typography>
                <strong>Budget:</strong> €{formData.budget}
              </Typography>
              <Typography>
                <strong>Experience:</strong> {formData.experience}
              </Typography>
              <Typography>
                <strong>Location Type:</strong> {formData.locationType}
              </Typography>
              <Divider sx={{ my: 2 }} />
              {techCategories.map(({ label, field }) => (
                <Typography key={field}>
                  <strong>{label}:</strong>{" "}
                  {(formData[field as keyof FormData] as string[]).join(", ")}
                </Typography>
              ))}
              <Typography>
                <strong>Other Tech:</strong> {formData.otherTech}
              </Typography>
              <Button
                variant="contained"
                color="primary"
                sx={{ mt: 2 }}
                onClick={handleSubmit}
              >
                Submit
              </Button>
            </CardContent>
          </Card>
        );
      default:
        return null;
    }
  };

  return (
    <div style={{ maxWidth: 600, margin: "auto", padding: 20 }}>
      <Stepper activeStep={activeStep} alternativeLabel>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>
      <div style={{ marginTop: 30 }}>{renderStepContent(activeStep)}</div>
      <div style={{ marginTop: 20 }}>
        {activeStep < steps.length - 1 && (
          <Button
            variant="contained"
            color="primary"
            onClick={() => {
              if (validateStep()) {
                setActiveStep((prev) => prev + 1);
              }
            }}
            sx={{ mr: 1 }}
          >
            Next
          </Button>
        )}
        {activeStep > 0 && (
          <Button onClick={() => setActiveStep((prev) => prev - 1)}>
            Back
          </Button>
        )}
      </div>
      <Snackbar
        open={submitted}
        autoHideDuration={6000}
        onClose={() => setSubmitted(false)}
      >
        <Alert
          onClose={() => setSubmitted(false)}
          severity="success"
          sx={{ width: "100%" }}
        >
          Project successfully submitted!
        </Alert>
      </Snackbar>
    </div>
  );
};

export default StepperForm;
