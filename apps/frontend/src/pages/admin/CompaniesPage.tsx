import React, { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  CircularProgress
} from '@mui/material'
import { AddRounded, BusinessRounded } from '@mui/icons-material'
import { adminApi } from '../../api/admin'
import type { Company } from '../../api/admin'

const CompaniesPage: React.FC = () => {
  const [companies, setCompanies] = useState<Company[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [newCompanyName, setNewCompanyName] = useState('')
  const [creating, setCreating] = useState(false)

  useEffect(() => {
    fetchCompanies()
  }, [])

  const fetchCompanies = async () => {
    try {
      const companiesData = await adminApi.getCompanies()
      setCompanies(companiesData)
      setLoading(false)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load companies')
      setLoading(false)
    }
  }

  const handleCreateCompany = async () => {
    if (!newCompanyName.trim()) return

    setCreating(true)
    setError('')

    try {
      const newCompany = await adminApi.createCompany({ name: newCompanyName })
      setCompanies(prev => [...prev, newCompany])
      setDialogOpen(false)
      setNewCompanyName('')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create company')
    } finally {
      setCreating(false)
    }
  }

  const handleDialogClose = () => {
    setDialogOpen(false)
    setNewCompanyName('')
    setError('')
  }

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="300px">
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">
          Companies Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddRounded />}
          onClick={() => setDialogOpen(true)}
        >
          Add Company
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Registered Companies
          </Typography>
          
          {companies.length === 0 ? (
            <Box 
              display="flex" 
              flexDirection="column" 
              alignItems="center" 
              py={4}
              color="text.secondary"
            >
              <BusinessRounded sx={{ fontSize: 64, mb: 2, opacity: 0.5 }} />
              <Typography variant="body1">
                No companies registered yet
              </Typography>
            </Box>
          ) : (
            <List>
              {companies.map((company, index) => (
                <ListItem 
                  key={company.id}
                  divider={index < companies.length - 1}
                  sx={{ pl: 0 }}
                >
                  <ListItemText
                    primary={company.name}
                    secondary={`Created: ${new Date(company.created_at).toLocaleDateString()}`}
                  />
                </ListItem>
              ))}
            </List>
          )}
        </CardContent>
      </Card>

      {/* Add Company Dialog */}
      <Dialog 
        open={dialogOpen} 
        onClose={handleDialogClose}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Add New Company</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="normal"
            label="Company Name"
            fullWidth
            variant="outlined"
            value={newCompanyName}
            onChange={(e) => setNewCompanyName(e.target.value)}
            disabled={creating}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDialogClose} disabled={creating}>
            Cancel
          </Button>
          <Button 
            onClick={handleCreateCompany}
            variant="contained"
            disabled={!newCompanyName.trim() || creating}
          >
            {creating ? <CircularProgress size={20} /> : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default CompaniesPage
