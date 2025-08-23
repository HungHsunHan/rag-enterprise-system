import React from 'react'
import { Box, AppBar, Toolbar, Typography, Button } from '@mui/material'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { LogoutRounded } from '@mui/icons-material'

interface LayoutProps {
  children: React.ReactNode
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const navigate = useNavigate()
  const { isAuthenticated, user, logout } = useAuthStore()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <Box sx={{ flexGrow: 1, minHeight: '100vh', bgcolor: 'background.default' }}>
      {isAuthenticated && (
        <AppBar position="static" elevation={0} sx={{ bgcolor: 'primary.main' }}>
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              HR Internal Q&A System
            </Typography>
            {user && (
              <Typography variant="body2" sx={{ mr: 2, opacity: 0.8 }}>
                {user.type === 'admin' ? 'Admin' : `Employee: ${user.employeeId}`}
              </Typography>
            )}
            <Button 
              color="inherit" 
              onClick={handleLogout}
              startIcon={<LogoutRounded />}
              sx={{ textTransform: 'none' }}
            >
              Logout
            </Button>
          </Toolbar>
        </AppBar>
      )}
      <Box component="main">
        {children}
      </Box>
    </Box>
  )
}

export default Layout
