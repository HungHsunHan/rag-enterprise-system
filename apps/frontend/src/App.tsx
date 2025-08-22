import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Container } from '@mui/material'
import { useAuthStore } from './store/authStore'
import LoginPage from './pages/LoginPage'
import AdminDashboard from './pages/AdminDashboard'
import ChatPage from './pages/ChatPage'
import Layout from './components/Layout'

function App() {
  const { isAuthenticated, user } = useAuthStore()

  return (
    <Layout>
      <Container maxWidth="lg" sx={{ py: 3 }}>
        <Routes>
          {/* Login Route */}
          <Route 
            path="/login" 
            element={
              isAuthenticated ? (
                user?.type === 'admin' ? (
                  <Navigate to="/admin" replace />
                ) : (
                  <Navigate to="/chat" replace />
                )
              ) : (
                <LoginPage />
              )
            } 
          />
          
          {/* Admin Routes */}
          <Route 
            path="/admin/*" 
            element={
              isAuthenticated && user?.type === 'admin' ? (
                <AdminDashboard />
              ) : (
                <Navigate to="/login" replace />
              )
            } 
          />
          
          {/* User Chat Route */}
          <Route 
            path="/chat" 
            element={
              isAuthenticated && user?.type === 'user' ? (
                <ChatPage />
              ) : (
                <Navigate to="/login" replace />
              )
            } 
          />
          
          {/* Default redirect */}
          <Route 
            path="/" 
            element={
              isAuthenticated ? (
                user?.type === 'admin' ? (
                  <Navigate to="/admin" replace />
                ) : (
                  <Navigate to="/chat" replace />
                )
              ) : (
                <Navigate to="/login" replace />
              )
            } 
          />
        </Routes>
      </Container>
    </Layout>
  )
}

export default App
