import React, { useState, useEffect } from 'react'
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
  Divider,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Alert
} from '@mui/material'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  DashboardRounded,
  BusinessRounded,
  FolderRounded,
  FeedbackRounded,
  StorageRounded,
  PeopleRounded,
  DescriptionRounded,
  QueryStatsRounded,
  ShareRounded
} from '@mui/icons-material'
import CompaniesPage from './admin/CompaniesPage'
import KnowledgeManagementPage from './admin/KnowledgeManagementPage'
import FeedbackDashboard from './admin/FeedbackDashboard'
import KnowledgeChunksPage from './admin/KnowledgeChunksPage'
import { adminApi, type DashboardMetrics, type CompanyMetrics } from '../api/admin'

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

const DashboardHome: React.FC = () => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setLoading(true)
        const data = await adminApi.getDashboardMetrics()
        setMetrics(data)
        setError(null)
      } catch (err) {
        setError('Failed to load dashboard metrics')
        console.error('Error fetching dashboard metrics:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchMetrics()
  }, [])

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
        <CircularProgress />
      </Box>
    )
  }

  if (error) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom>
          Welcome to Admin Dashboard
        </Typography>
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      </Box>
    )
  }

  if (!metrics) {
    return null
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Welcome to Admin Dashboard
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Manage companies, knowledge base, and monitor system performance.
      </Typography>

      {/* System Overview Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%' }}>
            <CardContent sx={{ height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <BusinessRounded color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6" noWrap>Total Companies</Typography>
              </Box>
              <Typography variant="h3" color="primary" sx={{ my: 1 }}>
                {metrics.total_companies}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Active tenant count
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%' }}>
            <CardContent sx={{ height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <ShareRounded color="secondary" sx={{ mr: 1 }} />
                <Typography variant="h6" noWrap>Shared Documents</Typography>
              </Box>
              <Typography variant="h3" color="secondary" sx={{ my: 1 }}>
                {metrics.shared_documents_count}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Cross-company resources
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%' }}>
            <CardContent sx={{ height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <PeopleRounded color="success" sx={{ mr: 1 }} />
                <Typography variant="h6" noWrap>Total Users</Typography>
              </Box>
              <Typography variant="h3" color="success.main" sx={{ my: 1 }}>
                {metrics.company_metrics.reduce((sum, company) => sum + company.user_count, 0)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                All employees
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%' }}>
            <CardContent sx={{ height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <QueryStatsRounded color="warning" sx={{ mr: 1 }} />
                <Typography variant="h6" noWrap>Queries Today</Typography>
              </Box>
              <Typography variant="h3" color="warning.main" sx={{ my: 1 }}>
                {metrics.company_metrics.reduce((sum, company) => sum + company.queries_today, 0)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                System activity
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Company Breakdown */}
      <Typography variant="h5" gutterBottom sx={{ mt: 4, mb: 2 }}>
        Company Breakdown
      </Typography>
      <Grid container spacing={3}>
        {metrics.company_metrics.map((company) => (
          <Grid item xs={12} md={6} lg={4} key={company.company_id}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom color="primary">
                  {company.company_name}
                </Typography>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <PeopleRounded fontSize="small" sx={{ mr: 0.5, color: 'text.secondary' }} />
                    <Typography variant="body2" color="text.secondary">Users:</Typography>
                  </Box>
                  <Typography variant="h6" color="success.main">{company.user_count}</Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <DescriptionRounded fontSize="small" sx={{ mr: 0.5, color: 'text.secondary' }} />
                    <Typography variant="body2" color="text.secondary">Documents:</Typography>
                  </Box>
                  <Typography variant="h6" color="info.main">{company.document_count}</Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <QueryStatsRounded fontSize="small" sx={{ mr: 0.5, color: 'text.secondary' }} />
                    <Typography variant="body2" color="text.secondary">Queries Today:</Typography>
                  </Box>
                  <Typography variant="h6" color="warning.main">{company.queries_today}</Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  )
}

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