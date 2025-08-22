import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import {
  Box,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  Divider
} from '@mui/material'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  DashboardRounded,
  BusinessRounded,
  FolderRounded,
  FeedbackRounded,
  StorageRounded
} from '@mui/icons-material'
import CompaniesPage from './admin/CompaniesPage'
import KnowledgeManagementPage from './admin/KnowledgeManagementPage'
import FeedbackDashboard from './admin/FeedbackDashboard'
import KnowledgeChunksPage from './admin/KnowledgeChunksPage'

const drawerWidth = 240

const AdminDashboard: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()

  const menuItems = [
    {
      text: 'Dashboard',
      icon: <DashboardRounded />,
      path: '/admin',
      exact: true
    },
    {
      text: 'Companies',
      icon: <BusinessRounded />,
      path: '/admin/companies'
    },
    {
      text: 'Knowledge Management',
      icon: <FolderRounded />,
      path: '/admin/knowledge'
    },
    {
      text: 'User Feedback',
      icon: <FeedbackRounded />,
      path: '/admin/feedback'
    },
    {
      text: 'Knowledge Base View',
      icon: <StorageRounded />,
      path: '/admin/embeddings'
    }
  ]

  const isSelected = (path: string, exact = false) => {
    if (exact) {
      return location.pathname === path
    }
    return location.pathname.startsWith(path)
  }

  const handleNavigation = (path: string) => {
    navigate(path)
  }

  return (
    <Box sx={{ display: 'flex' }}>
      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
            position: 'relative',
          },
        }}
      >
        <Box sx={{ p: 2 }}>
          <Typography variant="h6" color="primary">
            Admin Dashboard
          </Typography>
        </Box>
        <Divider />
        <List>
          {menuItems.map((item) => (
            <ListItem key={item.text} disablePadding>
              <ListItemButton
                selected={isSelected(item.path, item.exact)}
                onClick={() => handleNavigation(item.path)}
              >
                <ListItemIcon>{item.icon}</ListItemIcon>
                <ListItemText primary={item.text} />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </Drawer>
      
      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <Routes>
          <Route path="/" element={<DashboardHome />} />
          <Route path="/companies" element={<CompaniesPage />} />
          <Route path="/knowledge" element={<KnowledgeManagementPage />} />
          <Route path="/feedback" element={<FeedbackDashboard />} />
          <Route path="/embeddings" element={<KnowledgeChunksPage />} />
        </Routes>
      </Box>
    </Box>
  )
}

const DashboardHome: React.FC = () => (
  <Box>
    <Typography variant="h4" gutterBottom>
      Welcome to Admin Dashboard
    </Typography>
    <Typography variant="body1" color="text.secondary">
      Manage companies, knowledge base, and monitor system performance.
    </Typography>
  </Box>
)

const ComingSoon: React.FC<{ title: string }> = ({ title }) => (
  <Box>
    <Typography variant="h4" gutterBottom>
      {title}
    </Typography>
    <Typography variant="body1" color="text.secondary">
      This feature is coming soon...
    </Typography>
  </Box>
)

export default AdminDashboard