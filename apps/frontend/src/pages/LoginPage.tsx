import React, { useState } from 'react'
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Tab,
  Tabs,
  Alert,
  CircularProgress
} from '@mui/material'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { authApi } from '../api/auth'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel({ children, value, index, ...other }: TabPanelProps) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`login-tabpanel-${index}`}
      aria-labelledby={`login-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  )
}

const LoginPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  
  // Admin login form
  const [adminEmail, setAdminEmail] = useState('')
  const [adminPassword, setAdminPassword] = useState('')
  
  // User login form
  const [employeeId, setEmployeeId] = useState('')
  
  const navigate = useNavigate()
  const { login } = useAuthStore()

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue)
    setError('')
  }

  const handleAdminLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await authApi.adminLogin({
        email: adminEmail,
        password: adminPassword
      })
      
      // Mock user data - in real app, decode from JWT or fetch user info
      login(
        { id: '1', email: adminEmail, type: 'admin' },
        response.access_token
      )
      
      navigate('/admin')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Admin login failed')
    } finally {
      setLoading(false)
    }
  }

  const handleUserLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await authApi.userLogin({
        employee_id: employeeId
      })
      
      // Mock user data - in real app, decode from JWT or fetch user info
      login(
        { id: '1', employeeId: employeeId, type: 'user', companyId: '1' },
        response.access_token
      )
      
      navigate('/chat')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Employee login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box 
      display="flex" 
      justifyContent="center" 
      alignItems="center" 
      minHeight="100vh"
      bgcolor="background.default"
    >
      <Card sx={{ width: 400, maxWidth: '90vw' }}>
        <CardContent>
          <Typography variant="h4" component="h1" gutterBottom align="center">
            HR Q&A System
          </Typography>
          
          <Tabs value={activeTab} onChange={handleTabChange} variant="fullWidth">
            <Tab label="Employee Login" />
            <Tab label="Admin Login" />
          </Tabs>

          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}

          <TabPanel value={activeTab} index={0}>
            <form onSubmit={handleUserLogin}>
              <TextField
                fullWidth
                label="Employee ID"
                value={employeeId}
                onChange={(e) => setEmployeeId(e.target.value)}
                margin="normal"
                required
                disabled={loading}
              />
              <Button
                type="submit"
                fullWidth
                variant="contained"
                sx={{ mt: 2 }}
                disabled={loading || !employeeId}
              >
                {loading ? <CircularProgress size={24} /> : 'Login'}
              </Button>
            </form>
          </TabPanel>

          <TabPanel value={activeTab} index={1}>
            <form onSubmit={handleAdminLogin}>
              <TextField
                fullWidth
                label="Email"
                type="email"
                value={adminEmail}
                onChange={(e) => setAdminEmail(e.target.value)}
                margin="normal"
                required
                disabled={loading}
              />
              <TextField
                fullWidth
                label="Password"
                type="password"
                value={adminPassword}
                onChange={(e) => setAdminPassword(e.target.value)}
                margin="normal"
                required
                disabled={loading}
              />
              <Button
                type="submit"
                fullWidth
                variant="contained"
                sx={{ mt: 2 }}
                disabled={loading || !adminEmail || !adminPassword}
              >
                {loading ? <CircularProgress size={24} /> : 'Login'}
              </Button>
            </form>
          </TabPanel>
        </CardContent>
      </Card>
    </Box>
  )
}

export default LoginPage