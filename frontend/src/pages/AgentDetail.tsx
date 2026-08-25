// src/pages/AgentDetail.tsx
import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Paper,
  Chip,
  Button,
  IconButton,
  Grid,
  Card,
  CardContent,
  Divider,
  Tooltip,
} from '@mui/material';
import {
  ArrowBack,
  PlayArrow,
  Stop,
  Refresh,
  Code,
  Storage,
  Description,
  CheckCircle,
  Error,
  Pending,
} from '@mui/icons-material';

const agentDetails: Record<string, any> = {
  '1': {
    name: 'CEO Agent',
    role: 'Chief Executive Officer',
    status: 'running',
    model: 'llama3.2:3b',
    output: '605 chars',
    lastRun: '2024-01-15 14:30:25',
    description: 'Analyzes project requirements and creates project summaries.',
    files: ['ceo.md', 'project_summary.md'],
    memory: '1.2 KB',
  },
  '2': {
    name: 'CTO Agent',
    role: 'Chief Technology Officer',
    status: 'running',
    model: 'phi3.5:3.8b',
    output: '2,328 chars',
    lastRun: '2024-01-15 14:32:10',
    description: 'Designs system architecture and makes technical decisions.',
    files: ['system_architecture.md', 'cto.md'],
    memory: '2.4 KB',
  },
};

const AgentDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const agent = agentDetails[id || '1'];

  if (!agent) {
    return (
      <Box>
        <Typography variant="h5">Agent not found</Typography>
        <Button startIcon={<ArrowBack />} onClick={() => navigate('/agents')}>
          Back to Agents
        </Button>
      </Box>
    );
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return <CheckCircle sx={{ color: '#22c55e' }} />;
      case 'idle':
        return <Pending sx={{ color: '#f59e0b' }} />;
      case 'error':
        return <Error sx={{ color: '#ef4444' }} />;
      default:
        return <Pending />;
    }
  };

  const stats = [
    { label: 'Status', value: agent.status, icon: getStatusIcon(agent.status) },
    { label: 'Model', value: agent.model, icon: <Code /> },
    { label: 'Output', value: agent.output, icon: <Description /> },
    { label: 'Memory', value: agent.memory, icon: <Storage /> },
  ];

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <IconButton onClick={() => navigate('/agents')} sx={{ mr: 2 }}>
          <ArrowBack />
        </IconButton>

        <Typography variant="h4" sx={{ fontWeight: 600 }}>
          {agent.name}
        </Typography>

        <Chip
          label={agent.status}
          color={agent.status === 'running' ? 'success' : 'warning'}
          sx={{ ml: 2, textTransform: 'capitalize' }}
        />

        <Box sx={{ ml: 'auto' }}>
          <Tooltip title="Run Agent">
            <IconButton color="success">
              <PlayArrow />
            </IconButton>
          </Tooltip>

          <Tooltip title="Stop Agent">
            <IconButton color="error">
              <Stop />
            </IconButton>
          </Tooltip>

          <Tooltip title="Refresh">
            <IconButton color="primary">
              <Refresh />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      <Typography variant="body1" color="textSecondary" sx={{ mb: 3 }}>
        {agent.description}
      </Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        {stats.map((stat) => (
          <Grid size={{ xs: 6, sm: 3 }} key={stat.label}>
            <Paper
              sx={{
                p: 2,
                bgcolor: '#1e293b',
                textAlign: 'center',
              }}
            >
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  mb: 1,
                }}
              >
                {stat.icon}
              </Box>

              <Typography
                variant="caption"
                color="text.secondary"
                sx={{ display: 'block' }}
              >
                {stat.label}
              </Typography>

              <Typography
                variant="body1"
                sx={{
                  mt: 0.5,
                  fontWeight: 600,
                  wordBreak: 'break-word',
                }}
              >
                {stat.value}
              </Typography>
            </Paper>
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 8 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Agent Information
              </Typography>

              <Divider sx={{ mb: 2 }} />

              <Box sx={{ mb: 2 }}>
                <Typography variant="caption" color="text.secondary">
                  Role
                </Typography>
                <Typography variant="body1">
                  {agent.role}
                </Typography>
              </Box>

              <Box sx={{ mb: 2 }}>
                <Typography variant="caption" color="text.secondary">
                  Model
                </Typography>
                <Typography variant="body1">
                  {agent.model}
                </Typography>
              </Box>

              <Box>
                <Typography variant="caption" color="text.secondary">
                  Last Run
                </Typography>
                <Typography variant="body1">
                  {agent.lastRun}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Agent Files
              </Typography>

              <Divider sx={{ mb: 2 }} />

              {agent.files.map((file: string) => (
                <Box
                  key={file}
                  sx={{
                    py: 1,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1,
                  }}
                >
                  <Description fontSize="small" />
                  <Typography variant="body2">
                    {file}
                  </Typography>
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AgentDetail;


