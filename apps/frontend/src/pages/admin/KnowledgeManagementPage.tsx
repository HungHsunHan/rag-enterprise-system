import React, { useState, useRef } from 'react'
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Chip,
  Alert,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material'
import {
  UploadFileRounded,
  DeleteRounded,
  FolderRounded,
  DescriptionRounded
} from '@mui/icons-material'

interface KnowledgeDocument {
  id: string
  file_name: string
  status: 'PROCESSING' | 'COMPLETED' | 'FAILED'
  company_id: string
  uploaded_at: string
}

const KnowledgeManagementPage: React.FC = () => {
  const [documents, setDocuments] = useState<KnowledgeDocument[]>([])
  const [selectedCompany, setSelectedCompany] = useState('')
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [documentToDelete, setDocumentToDelete] = useState<string | null>(null)
  
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Mock companies data
  const companies = [
    { id: '1', name: 'Acme Corporation' },
    { id: '2', name: 'Tech Innovators Ltd' }
  ]

  const handleCompanyChange = (companyId: string) => {
    setSelectedCompany(companyId)
    // TODO: Fetch documents for selected company
    // fetchDocuments(companyId)
    
    // Mock documents for now
    setDocuments([
      {
        id: '1',
        file_name: 'Employee Handbook.pdf',
        status: 'COMPLETED',
        company_id: companyId,
        uploaded_at: '2025-01-15T10:00:00Z'
      },
      {
        id: '2',
        file_name: 'HR Policies.docx',
        status: 'PROCESSING',
        company_id: companyId,
        uploaded_at: '2025-01-20T14:30:00Z'
      },
      {
        id: '3',
        file_name: 'Benefits Guide.txt',
        status: 'FAILED',
        company_id: companyId,
        uploaded_at: '2025-01-18T09:15:00Z'
      }
    ])
  }

  const handleFileSelect = () => {
    if (!selectedCompany) {
      setError('Please select a company first')
      return
    }
    fileInputRef.current?.click()
  }

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    setUploading(true)
    setError('')

    try {
      // TODO: Call actual API
      // const formData = new FormData()
      // formData.append('file', file)
      // const response = await adminApi.uploadDocument(selectedCompany, formData)
      
      // Mock upload for now
      const newDocument: KnowledgeDocument = {
        id: Date.now().toString(),
        file_name: file.name,
        status: 'PROCESSING',
        company_id: selectedCompany,
        uploaded_at: new Date().toISOString()
      }
      
      setDocuments(prev => [newDocument, ...prev])
      
      // Simulate processing
      setTimeout(() => {
        setDocuments(prev => 
          prev.map(doc => 
            doc.id === newDocument.id ? { ...doc, status: 'COMPLETED' } : doc
          )
        )
      }, 3000)
      
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload document')
    } finally {
      setUploading(false)
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  const handleDeleteDocument = async (documentId: string) => {
    try {
      // TODO: Call actual API
      // await adminApi.deleteDocument(documentId)
      
      setDocuments(prev => prev.filter(doc => doc.id !== documentId))
      setDeleteDialogOpen(false)
      setDocumentToDelete(null)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete document')
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'COMPLETED': return 'success'
      case 'PROCESSING': return 'warning'
      case 'FAILED': return 'error'
      default: return 'default'
    }
  }

  const getFileIcon = (fileName: string) => {
    const extension = fileName.split('.').pop()?.toLowerCase()
    return <DescriptionRounded />
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Knowledge Base Management
      </Typography>

      {/* Company Selection */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <FormControl fullWidth>
            <InputLabel>Select Company</InputLabel>
            <Select
              value={selectedCompany}
              onChange={(e) => handleCompanyChange(e.target.value)}
              label="Select Company"
            >
              {companies.map((company) => (
                <MenuItem key={company.id} value={company.id}>
                  {company.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </CardContent>
      </Card>

      {selectedCompany && (
        <>
          {/* Upload Section */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">
                  Upload Documents
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<UploadFileRounded />}
                  onClick={handleFileSelect}
                  disabled={uploading}
                >
                  Upload File
                </Button>
              </Box>
              
              {uploading && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Uploading and processing document...
                  </Typography>
                  <LinearProgress />
                </Box>
              )}

              <Typography variant="body2" color="text.secondary">
                Supported formats: PDF, DOCX, TXT (max 10MB)
              </Typography>
            </CardContent>
          </Card>

          {/* Error Alert */}
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {/* Documents List */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Knowledge Documents
              </Typography>
              
              {documents.length === 0 ? (
                <Box 
                  display="flex" 
                  flexDirection="column" 
                  alignItems="center" 
                  py={4}
                  color="text.secondary"
                >
                  <FolderRounded sx={{ fontSize: 64, mb: 2, opacity: 0.5 }} />
                  <Typography variant="body1">
                    No documents uploaded yet
                  </Typography>
                </Box>
              ) : (
                <List>
                  {documents.map((document, index) => (
                    <ListItem 
                      key={document.id}
                      divider={index < documents.length - 1}
                      sx={{ pl: 0 }}
                    >
                      <Box sx={{ mr: 2 }}>
                        {getFileIcon(document.file_name)}
                      </Box>
                      <ListItemText
                        primary={document.file_name}
                        secondary={`Uploaded: ${new Date(document.uploaded_at).toLocaleDateString()}`}
                      />
                      <Box sx={{ mr: 2 }}>
                        <Chip
                          label={document.status}
                          color={getStatusColor(document.status) as any}
                          size="small"
                        />
                      </Box>
                      <ListItemSecondaryAction>
                        <IconButton
                          edge="end"
                          onClick={() => {
                            setDocumentToDelete(document.id)
                            setDeleteDialogOpen(true)
                          }}
                          color="error"
                        >
                          <DeleteRounded />
                        </IconButton>
                      </ListItemSecondaryAction>
                    </ListItem>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </>
      )}

      {/* Hidden file input */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileUpload}
        accept=".pdf,.docx,.txt"
        style={{ display: 'none' }}
      />

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
      >
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete this document? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>
            Cancel
          </Button>
          <Button
            onClick={() => documentToDelete && handleDeleteDocument(documentToDelete)}
            color="error"
            variant="contained"
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default KnowledgeManagementPage