import React, { useEffect, useState } from "react";
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  CardActionArea,
  Button,
  Box,
  Divider,
} from "@mui/material";
import "./development-tasks-page.scss";
import { useLocation } from "react-router-dom";

interface Category {
  name: string;
  tech: string[];
}

interface Ticket {
  summary: string;
  description: string;
}

const PushedTicketsPage: React.FC = () => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [tasks, setTasks] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [generating, setGenerating] = useState<boolean>(false);
  const [codeSnippet, setCodeSnippet] = useState<string | null>(null);
  const location = useLocation();
  let { projectMarkdown } = location.state || {};

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await fetch(
          "http://localhost:8000/api/get-dev-categories",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ final_plan: projectMarkdown }),
          }
        );

        const data = await response.json();
        setCategories(data.categories || []);
      } catch (error) {
        console.error("Failed to fetch categories:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchCategories();
  }, [projectMarkdown]);

  const fetchTasks = async (category: string) => {
    setSelectedCategory(category);
    setTasks([]);
    setCodeSnippet(null);
    setGenerating(true);

    try {
      const response = await fetch(
        "http://localhost:8000/api/get-tasks-by-category",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ category, final_plan: projectMarkdown }),
        }
      );

      const data = await response.json();
      setTasks(data.tasks || []);
    } catch (error) {
      console.error("Failed to fetch tasks:", error);
    } finally {
      setGenerating(false);
    }
  };

  const handleCardClick = async (ticket: Ticket) => {
    setGenerating(true);
    setCodeSnippet(null);

    try {
      const response = await fetch(
        "http://localhost:8000/api/generate-code-snippet",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            task_name: ticket.summary,
            task_description: ticket.description,
            final_plan: projectMarkdown,
          }),
        }
      );

      const data = await response.json();
      setCodeSnippet(data.snippet || "No snippet returned.");
    } catch (error) {
      console.error("Failed to generate code snippet:", error);
      setCodeSnippet("Error generating snippet.");
    } finally {
      setGenerating(false);
    }
  };

  return (
    <Container className="pushed-tickets-container">
      {loading ? (
        <CircularProgress />
      ) : (
        <>
          <Typography variant="h5" gutterBottom>
            Select a category to view development tasks
          </Typography>
          <Box display="flex" gap={2} flexWrap="wrap" mb={3}>
            {categories.map((cat) => (
              <Button
                key={cat.name}
                variant={
                  selectedCategory === cat.name ? "contained" : "outlined"
                }
                onClick={() => fetchTasks(cat.name)}
              >
                {cat.name} ({cat.tech.join(", ")})
              </Button>
            ))}
          </Box>

          {generating ? (
            <CircularProgress />
          ) : (
            <>
              {selectedCategory && (
                <>
                  <Typography variant="h6" gutterBottom>
                    Tasks for: {selectedCategory}
                  </Typography>
                  <Divider sx={{ mb: 2 }} />
                </>
              )}

              <div className="card-grid">
                {tasks.map((ticket, index) => (
                  <div className="card-item" key={index}>
                    <Card className="ticket-card">
                      <CardActionArea
                        onClick={() => handleCardClick(ticket)}
                        sx={{ height: "100%" }}
                      >
                        <CardContent className="card-content">
                          <Typography variant="h6" gutterBottom>
                            {ticket.summary}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {ticket.description}
                          </Typography>
                        </CardContent>
                      </CardActionArea>
                    </Card>
                  </div>
                ))}
              </div>
            </>
          )}

          {codeSnippet && (
            <Box mt={4} p={2} bgcolor="#f4f4f4" borderRadius={2}>
              <Typography variant="h6" gutterBottom>
                Generated Code Snippet
              </Typography>
              <pre style={{ whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
                {codeSnippet}
              </pre>
            </Box>
          )}
        </>
      )}
    </Container>
  );
};

export default PushedTicketsPage;
