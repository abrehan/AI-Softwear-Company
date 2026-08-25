// src/pages/Workspace.tsx
import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  List,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Collapse,
  IconButton,
  Chip,
  TextField,
  InputAdornment,
  Grid,
} from '@mui/material';
import {
  Folder,
  FolderOpen,
  Description,
  Code,
  Image,
  ExpandLess,
  ExpandMore,
  Search,
  Download,
  CreateNewFolder,
} from '@mui/icons-material';

interface FileItem {
  name: string;
  type: 'file' | 'folder';
  size?: string;
  children?: FileItem[];
  icon?: React.ReactNode;
}

const workspaceData: FileItem[] = [
  {
    name: 'architecture',
    type: 'folder',
    children: [
      { name: 'system_architecture.md', type: 'file', size: '2.3 KB' },
      { name: 'architect_design.md', type: 'file', size: '2.5 KB' },
    ],
  },
  {
    name: 'project',
    type: 'folder',
    children: [
      { name: 'complete_plan_with_pm.md', type: 'file', size: '4.5 KB' },
      { name: 'pm_plan.md', type: 'file', size: '2.1 KB' },
      { name: 'deliverable_complete.md', type: 'file', size: '8.2 KB' },
    ],
  },
  {
    name: 'code',
    type: 'folder',
    children: [
      {
        name: 'backend',
        type: 'folder',
        children: [
          { name: 'main.py', type: 'file', size: '120 B' },
          { name: 'database.py', type: 'file', size: '760 B' },
          { name: 'config.py', type: 'file', size: '519 B' },
          { name: 'security.py', type: 'file', size: '544 B' },
        ],
      },
      { name: 'generated_code.md', type: 'file', size: '1.2 KB' },
    ],
  },
  {
    name: 'documentation',
    type: 'folder',
    children: [
      { name: 'technical_docs.md', type: 'file', size: '3.4 KB' },
    ],
  },
  {
    name: 'frontend',
    type: 'folder',
    children: [
      { name: 'frontend_design.md', type: 'file', size: '2.5 KB' },
    ],
  },
  {
    name: 'database',
    type: 'folder',
    children: [
      { name: 'database_design.md', type: 'file', size: '2.5 KB' },
    ],
  },
  {
    name: 'devops',
    type: 'folder',
    children: [
      { name: 'devops_deployment.md', type: 'file', size: '2.5 KB' },
    ],
  },
  {
    name: 'security',
    type: 'folder',
    children: [
      { name: 'devsecops_strategy.md', type: 'file', size: '2.5 KB' },
      { name: 'security_report.md', type: 'file', size: '2.8 KB' },
    ],
  },
  {
    name: 'support',
    type: 'folder',
    children: [
      { name: 'customer_support.md', type: 'file', size: '2.4 KB' },
    ],
  },
  {
    name: 'files',
    type: 'folder',
    children: [
      { name: 'generated_file_structure.md', type: 'file', size: '1.5 KB' },
    ],
  },
];

const FileTreeItem: React.FC<{ item: FileItem; depth?: number }> = ({ item, depth = 0 }) => {
  const [open, setOpen] = useState(true);

  const handleToggle = () => {
    if (item.type === 'folder') {
      setOpen(!open);
    }
  };

  const getIcon = (item: FileItem) => {
    if (item.type === 'folder') {
      return open ? <FolderOpen /> : <Folder />;
    }
    if (item.name.endsWith('.md')) return <Description />;
    if (item.name.endsWith('.py') || item.name.endsWith('.ts')) return <Code />;
    if (item.name.endsWith('.png') || item.name.endsWith('.jpg')) return <Image />;
    return <Description />;
  };

  return (
    <>
      <ListItemButton onClick={handleToggle} sx={{ pl: depth * 2 + 2 }}>
        <ListItemIcon>{getIcon(item)}</ListItemIcon>
        <ListItemText
          primary={item.name}
          secondary={item.size}
          slotProps={{
            secondary: {
              variant: 'caption',
            },
          }}
        />
        {item.type === 'folder' && (
          <IconButton size="small">
            {open ? <ExpandLess /> : <ExpandMore />}
          </IconButton>
        )}
      </ListItemButton>
      {item.type === 'folder' && item.children && (
        <Collapse in={open} timeout="auto" unmountOnExit>
          <List component="div" disablePadding>
            {item.children.map((child, index) => (
              <FileTreeItem key={index} item={child} depth={depth + 1} />
            ))}
          </List>
        </Collapse>
      )}
    </>
  );
};

const Workspace: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');

  const fileStats = [
    { label: 'Total Files', value: '84' },
    { label: 'Total Size', value: '92.1 KB' },
    { label: 'Folders', value: '12' },
    { label: 'Generated Code', value: '15 files' },
  ];

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 600 }}>
          📁 Workspace
        </Typography>
        <Box>
          <IconButton color="primary">
            <CreateNewFolder />
          </IconButton>
          <IconButton color="primary">
            <Download />
          </IconButton>
        </Box>
      </Box>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        {fileStats.map((stat) => (
          <Grid size={{ xs: 6, sm: 3 }} key={stat.label}>
            <Paper sx={{ p: 2, bgcolor: '#1e293b', textAlign: 'center' }}>
              <Typography variant="h6" sx={{ fontWeight: 700 }}>
                {stat.value}
              </Typography>
              <Typography variant="caption" color="textSecondary">
                {stat.label}
              </Typography>
            </Paper>
          </Grid>
        ))}
      </Grid>

      <TextField
        fullWidth
        variant="outlined"
        placeholder="Search files..."
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

      <Paper sx={{ bgcolor: '#1e293b', maxHeight: 600, overflow: 'auto' }}>
        <List>
          {workspaceData.map((item, index) => (
            <FileTreeItem key={index} item={item} />
          ))}
        </List>
      </Paper>

      <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
        <Chip label="84 files" size="small" />
        <Chip label="92.1 KB" size="small" />
        <Chip label="15 Python files" size="small" />
        <Chip label="69 Markdown files" size="small" />
      </Box>
    </Box>
  );
};

export default Workspace;





