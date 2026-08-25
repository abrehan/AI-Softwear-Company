// src/pages/Agents.tsx
import React, { useState } from 'react';
import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  TextField,
  InputAdornment,
  Box,
  Typography,
  Tooltip,
  Button,
} from '@mui/material';
import { Search, PlayArrow, Stop, Refresh, Code, Storage, Security } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const agentsData = [
  { id: 1, name: 'CEO Agent', role: 'Chief Executive Officer', status: 'running', output: '605 chars', model: 'llama3.2:3b' },
  { id: 2, name: 'CTO Agent', role: 'Chief Technology Officer', status: 'running', output: '2,328 chars', model: 'phi3.5:3.8b' },
  { id: 3, name: 'PM Agent', role: 'Project Manager', status: 'running', output: '2,125 chars', model: 'llama3.2:3b' },
  { id: 4, name: 'Frontend Agent', role: 'Frontend Engineer', status: 'running', output: '2,485 chars', model: 'llama3.2:3b' },
  { id: 5, name: 'Backend Agent', role: 'Backend Engineer', status: 'running', output: '530 chars', model: 'qwen2.5-coder:7b' },
  { id: 6, name: 'Database Agent', role: 'Database Architect', status: 'running', output: '2,508 chars', model: 'qwen2.5-coder:0.5b' },
  { id: 7, name: 'DevOps Agent', role: 'DevOps Engineer', status: 'running', output: '2,508 chars', model: 'llama3.2:3b' },
  { id: 8, name: 'DevSecOps Agent', role: 'DevSecOps Engineer', status: 'running', output: '2,462 chars', model: 'llama3.2:1b' },
  { id: 9, name: 'QA Agent', role: 'QA Engineer', status: 'running', output: '2,520 chars', model: 'llama3.2:3b' },
  { id: 10, name: 'Security Agent', role: 'Security Engineer', status: 'running', output: '2,757 chars', model: 'llama3.2:1b' },
  { id: 11, name: 'Architect Agent', role: 'System Architect', status: 'running', output: '2,543 chars', model: 'llama3.2:3b' },
  { id: 12, name: 'Documentation Agent', role: 'Technical Writer', status: 'running', output: '39 chars', model: 'llama3.2:3b' },
  { id: 13, name: 'File Generator Agent', role: 'File Generator', status: 'running', output: '1,479 chars', model: 'llama3.2:3b' },
];

const Agents: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const navigate = useNavigate();

  const filteredAgents = agentsData.filter((agent) =>
    agent.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    agent.role.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'success';
      case 'idle': return 'warning';
      case 'error': return 'error';
      default: return 'default';
    }
  };

  const getAgentIcon = (name: string) => {
    if (name.includes('CEO') || name.includes('CTO') || name.includes('PM')) return <Code />;
    if (name.includes('Frontend') || name.includes('Backend')) return <Code />;
    if (name.includes('Database')) return <Storage />;
    if (name.includes('Security') || name.includes('DevSecOps')) return <Security />;
    return <Code />;
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 600 }}>
          🤖 Agents
        </Typography>
        <Box>
          <Button
            variant="contained"
            startIcon={<PlayArrow />}
            sx={{ mr: 2 }}
            color="success"
          >
            Run All
          </Button>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
          >
            Refresh
          </Button>
        </Box>
      </Box>

      <TextField
        fullWidth
        variant="outlined"
        placeholder="Search agents..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        sx={{ mb: 3 }}
slotProps={{
  input: {
    startAdornment: (
      <InputAdornment position="start">
        <Search />
      </InputAdornment>
    ),
  },
}}
/>

      <TableContainer component={Paper} sx={{ bgcolor: '#1e293b' }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Agent</TableCell>
              <TableCell>Role</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Output</TableCell>
              <TableCell>Model</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredAgents.map((agent) => (
              <TableRow
                key={agent.id}
                sx={{
                  '&:hover': {
                    bgcolor: 'rgba(99, 102, 241, 0.05)',
                    cursor: 'pointer',
                  },
                }}
                onClick={() => navigate(`/agents/${agent.id}`)}
              >
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Box sx={{ mr: 1, color: '#6366f1' }}>{getAgentIcon(agent.name)}</Box>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>
                      {agent.name}
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell>{agent.role}</TableCell>
                <TableCell>
                  <Chip
                    label={agent.status}
                    color={getStatusColor(agent.status) as any}
                    size="small"
                    sx={{ textTransform: 'capitalize' }} />
                </TableCell>
                <TableCell>{agent.output}</TableCell>
                <TableCell>
                  <Chip label={agent.model} size="small" variant="outlined" />
                </TableCell>
                <TableCell>
                  <Tooltip title="Run">
                    <IconButton size="small" color="success">
                      <PlayArrow />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Stop">
                    <IconButton size="small" color="error">
                      <Stop />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="View Details">
                    <IconButton size="small" color="primary">
                      <Refresh />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Typography variant="body2" color="textSecondary" sx={{ mt: 2 }}>
        Showing {filteredAgents.length} of {agentsData.length} agents
      </Typography>
    </Box>
  );
};

export default Agents;

