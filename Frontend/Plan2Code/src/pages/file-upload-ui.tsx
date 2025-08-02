import React, { useState } from "react";
import {
  Box,
  Button,
  Typography,
  Card,
  TextField,
  Chip,
  Paper,
  Tabs,
  Tab,
} from "@mui/material";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import DescriptionIcon from "@mui/icons-material/Description";
import * as pdfjsLib from "pdfjs-dist/legacy/build/pdf";
import { Viewer, Worker } from "@react-pdf-viewer/core";
import "@react-pdf-viewer/core/lib/styles/index.css";
import { useNavigate } from "react-router-dom";

pdfjsLib.GlobalWorkerOptions.workerSrc =
  "https://unpkg.com/pdfjs-dist@3.0.279/build/pdf.worker.min.js";

const TextFileUpload: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [textContent, setTextContent] = useState<string>("");
  const [tabIndex, setTabIndex] = useState(0);
  const navigate = useNavigate();

  const handleSubmit = () => {
    if (textContent.trim()) {
      navigate("/results", { state: { text: textContent } });
    }
  };

  const handleTabChange = (_: React.SyntheticEvent, value: number) => {
    setTabIndex(value);
  };

  const handleFileChange = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const selectedFile = event.target.files?.[0];
    setFile(selectedFile || null);
    setTextContent("");

    if (!selectedFile) return;

    const extension = selectedFile.name.split(".").pop()?.toLowerCase() || "";

    // PDF parsing
    if (extension === "pdf") {
      const reader = new FileReader();
      reader.onload = async (e) => {
        const typedArray = new Uint8Array(e.target?.result as ArrayBuffer);
        const pdf = await pdfjsLib.getDocument(typedArray).promise;
        let text = "";
        for (let i = 1; i <= pdf.numPages; i++) {
          const page = await pdf.getPage(i);
          const content = await page.getTextContent();
          const pageText = content.items.map((item: any) => item.str).join(" ");
          text += pageText + "\n\n";
        }
        setTextContent(text);
      };
      reader.readAsArrayBuffer(selectedFile);
    }
    // Text-like files
    else if (
      selectedFile.type.startsWith("text") ||
      ["json", "csv", "md"].includes(extension)
    ) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setTextContent(e.target?.result as string);
      };
      reader.readAsText(selectedFile);
    }
  };

  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      p={4}
      sx={{ bgcolor: "background.default", minHeight: "100vh" }}
    >
      <Paper
        elevation={4}
        sx={{ p: 4, maxWidth: 720, width: "100%", textAlign: "center" }}
      >
        <Typography variant="h4" color="primary" gutterBottom>
          📁 Universal File Upload
        </Typography>
        <label htmlFor="file-upload">
          <input
            id="file-upload"
            type="file"
            accept="*"
            onChange={handleFileChange}
            style={{ display: "none" }}
          />
          <Button
            variant="contained"
            startIcon={<CloudUploadIcon />}
            component="span"
            sx={{ mt: 2, mb: 2 }}
          >
            Choose File
          </Button>
        </label>

        {file && (
          <Box
            display="flex"
            justifyContent="center"
            alignItems="center"
            gap={2}
            mt={2}
          >
            <Chip
              icon={<DescriptionIcon />}
              label={`Type: ${file.type || "unknown"}`}
              color="secondary"
              variant="outlined"
            />
            <Typography variant="body1">
              Selected: <strong>{file.name}</strong>
            </Typography>
          </Box>
        )}

        {file && (
          <>
            <Tabs
              value={tabIndex}
              onChange={handleTabChange}
              variant="fullWidth"
              sx={{ mt: 4 }}
            >
              <Tab label="👀 Visual Preview" />
              <Tab label="🔍 Text Content" />
            </Tabs>

            {/* Visual preview for PDF only */}
            <Box hidden={tabIndex !== 0} sx={{ mt: 2 }}>
              {file.name.endsWith(".pdf") ? (
                <Card sx={{ p: 2 }}>
                  <Worker workerUrl="https://unpkg.com/pdfjs-dist@3.0.279/build/pdf.worker.min.js">
                    <Viewer fileUrl={URL.createObjectURL(file)} />
                  </Worker>
                </Card>
              ) : (
                <Card sx={{ p: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    No visual preview available for this file type.
                  </Typography>
                </Card>
              )}
            </Box>

            {/* Text preview if extractable */}
            <Box hidden={tabIndex !== 1} sx={{ mt: 2 }}>
              <Card sx={{ p: 2 }}>
                {textContent ? (
                  <TextField
                    multiline
                    fullWidth
                    value={textContent}
                    rows={12}
                    variant="outlined"
                    InputProps={{ readOnly: true }}
                    sx={{
                      fontFamily: "monospace",
                      maxHeight: 400,
                      overflowY: "auto",
                      bgcolor: "background.paper",
                    }}
                  />
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    Text preview not available.
                  </Typography>
                )}
              </Card>
            </Box>
            {textContent && (
              <Button
                variant="contained"
                color="success"
                onClick={handleSubmit}
                sx={{ mt: 2 }}
              >
                Submit to Results
              </Button>
            )}
          </>
        )}
      </Paper>
    </Box>
  );
};

export default TextFileUpload;
