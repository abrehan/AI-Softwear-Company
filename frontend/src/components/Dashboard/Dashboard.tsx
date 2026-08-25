// src/pages/Dashboard.tsx
import React, { useState } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  People,
  Folder,
  CheckCircle,
  Error,
  Refresh,
  Code,
  Storage,
  Security,
  Dashboard as DashboardIcon,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

interface DashboardStats {
  totalAgents: number;
  activeAgents: number;
  failedAgents: number;
  totalFiles: number;
  totalCodeSize: number;
}

const Dashboard: React.FC = () => {
  const [stats] = useState<DashboardStats>({
    totalAgents: 34,
    activeAgents: 30,
    failedAgents: 3,
    totalFiles: 84,
    totalCodeSize: 94332,
  });

  const { refetch } = useQuery({
    queryKey: ['agents'],
    queryFn: async () => {
      const response = await axios.get('/backend/api/agents');
      return response.data;
    },
    enabled: false,
  });

  const statCards = [
    { title: 'Total Agents', value: stats.totalAgents, icon: <People />, color: '#6366f1' },
    { title: 'Active Agents', value: stats.activeAgents, icon: <CheckCircle />, color: '#22c55e' },
    { title: 'Failed Agents', value: stats.failedAgents, icon: <Error />, color: '#ef4444' },
    { title: 'Generated Files', value: stats.totalFiles, icon: <Folder />, color: '#f59e0b' },
  ];

  const agentCategories = [
    { name: 'Leadership', count: 5, icon: <DashboardIcon /> },
    { name: 'Development', count: 6, icon: <Code /> },
    { name: 'Database & DevOps', count: 5, icon: <Storage /> },
    { name: 'Security & QA', count: 4, icon: <Security /> },
    { name: 'Business', count: 6, icon: <People /> },
    { name: 'Creative & Content', count: 5, icon: <Folder /> },
    { name: 'Support', count: 3, icon: <People /> },
  ];

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 600 }}>
          🏢 Virtual Office Dashboard
        </Typography>
        <Tooltip title="Refresh">
          <IconButton onClick={() => refetch()} color="primary">
            <Refresh />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {statCards.map((stat) => (
          <Grid size={{ xs: 12, sm: 6, md: 3 }} key={stat.title}>
            <Paper
              sx={{
                p: 3,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
                border: '1px solid rgba(99, 102, 241, 0.1)',
              }}
            >
              <Box>
                <Typography variant="body2" color="textSecondary">
                  {stat.title}
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 700, mt: 1 }}>
                  {stat.value}
                </Typography>
              </Box>
              <Box
                sx={{
                  p: 2,
                  borderRadius: '50%',
                  bgcolor: `${stat.color}20`,
                  color: stat.color,
                }}
              >
                {stat.icon}
              </Box>
            </Paper>
          </Grid>
        ))}
      </Grid>

      {/* Agent Categories */}
      <Typography variant="h5" sx={{ mb: 2, fontWeight: 600 }}>
        Agent Categories
      </Typography>
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {agentCategories.map((category) => (
          <Grid size={{ xs: 12, sm: 6, md: 4 }} key={category.name}>
            <Card
              sx={{
                bgcolor: '#1e293b',
                border: '1px solid rgba(99, 102, 241, 0.1)',
                transition: 'transform 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  borderColor: 'rgba(99, 102, 241, 0.3)',
                },
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Box sx={{ mr: 1, color: '#6366f1' }}>{category.icon}</Box>
                  <Typography variant="h6">{category.name}</Typography>
                </Box>
                <Typography variant="body2" color="textSecondary">
                  {category.count} agents
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={(category.count / 34) * 100}
                  sx={{ mt: 2, height: 6, borderRadius: 3 }}
                />
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Quick Actions */}
      <Paper sx={{ p: 3, bgcolor: '#1e293b', border: '1px solid rgba(99, 102, 241, 0.1)' }}>
        <Typography variant="h5" sx={{ mb: 2, fontWeight: 600 }}>
          Quick Actions
        </Typography>
        <Grid container spacing={2}>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Card sx={{ bgcolor: '#0f172a', cursor: 'pointer', '&:hover': { bgcolor: '#1a2332' } }}>
              <CardContent>
                <Typography variant="body2" color="textSecondary">
                  Run All Agents
                </Typography>
                <Chip label="34 agents" size="small" color="primary" sx={{ mt: 1 }} />
              </CardContent>
            </Card>
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Card sx={{ bgcolor: '#0f172a', cursor: 'pointer', '&:hover': { bgcolor: '#1a2332' } }}>
              <CardContent>
                <Typography variant="body2" color="textSecondary">
                  View Generated Code
                </Typography>
                <Chip label="15 files" size="small" color="success" sx={{ mt: 1 }} />
              </CardContent>
            </Card>
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Card sx={{ bgcolor: '#0f172a', cursor: 'pointer', '&:hover': { bgcolor: '#1a2332' } }}>
              <CardContent>
                <Typography variant="body2" color="textSecondary">
                  View Documentation
                </Typography>
                <Chip label="84 files" size="small" color="warning" sx={{ mt: 1 }} />
              </CardContent>
            </Card>
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Card sx={{ bgcolor: '#0f172a', cursor: 'pointer', '&:hover': { bgcolor: '#1a2332' } }}>
              <CardContent>
                <Typography variant="body2" color="textSecondary">
                  System Status
                </Typography>
                <Chip label="88% healthy" size="small" color="info" sx={{ mt: 1 }} />
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
};

export default Dashboard;





