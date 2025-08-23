import React, { useState, useRef, useEffect } from 'react'
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
  MenuItem,
  Checkbox,
  ListItemIcon,
  Toolbar,
  Snackbar
} from '@mui/material'
import {
  UploadFileRounded,
  DeleteRounded,
  FolderRounded,
  DescriptionRounded,
  DeleteSweepRounded,
  SelectAll
} from '@mui/icons-material'
import { adminApi } from '../../api/admin'
import type { Company, KnowledgeDocument } from '../../api/admin'

const KnowledgeManagementPage: React.FC = () => {
  const [documents, setDocuments] = useState<KnowledgeDocument[]>([])
  const [companies, setCompanies] = useState<Company[]>([])
  const [selectedCompany, setSelectedCompany] = useState('')
  const [uploading, setUploading] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [documentToDelete, setDocumentToDelete] = useState<string | null>(null)
  const [selectedDocuments, setSelectedDocuments] = useState<Set<string>>(new Set())
  const [bulkDeleteDialogOpen, setBulkDeleteDialogOpen] = useState(false)
  const [successMessage, setSuccessMessage] = useState('')
  
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Load companies on component mount
  useEffect(() => {
    loadCompanies()
  }, [])

  const loadCompanies = async () => {
    try {
      const companiesData = await adminApi.getCompanies()
      setCompanies(companiesData)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load companies')
    }
  }


  const loadDocuments = async (companyId: string) => {
    setLoading(true)
    setError('')
    try {
      const documentsData = await adminApi.getDocuments(companyId)
      setDocuments(documentsData)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load documents')
    } finally {
      setLoading(false)
    }
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
      const response = await adminApi.uploadDocument(selectedCompany, file)
      
      // Refresh documents list
      await loadDocuments(selectedCompany)
      
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
      await adminApi.deleteDocument(documentId)
      
      // Refresh documents list
      if (selectedCompany) {
        await loadDocuments(selectedCompany)
      }
      
      setDeleteDialogOpen(false)
      setDocumentToDelete(null)
      setSuccessMessage('Document deleted successfully')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete document')
    }
  }

  const handleDocumentSelect = (documentId: string) => {
    const newSelected = new Set(selectedDocuments)
    if (newSelected.has(documentId)) {
      newSelected.delete(documentId)
    } else {
      newSelected.add(documentId)
    }
    setSelectedDocuments(newSelected)
  }

  const handleSelectAll = () => {
    if (selectedDocuments.size === documents.length) {
      setSelectedDocuments(new Set())
    } else {
      setSelectedDocuments(new Set(documents.map(doc => doc.id)))
    }
  }

  const handleBulkDelete = async () => {
    if (selectedDocuments.size === 0) return

    try {
      const documentIds = Array.from(selectedDocuments)
      const result = await adminApi.bulkDeleteDocuments(selectedCompany, documentIds)
      
      // Refresh documents list
      await loadDocuments(selectedCompany)
      
      setSelectedDocuments(new Set())
      setBulkDeleteDialogOpen(false)
      
      // Show success message with details
      const { success_count, failed_count } = result.details
      setSuccessMessage(`Bulk delete completed: ${success_count} documents deleted successfully${failed_count > 0 ? `, ${failed_count} failed` : ''}`)
      
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete documents')
    }
  }

  const handleCompanyChange = (companyId: string) => {
    setSelectedCompany(companyId)
    setSelectedDocuments(new Set()) // Clear selection when changing company
    if (companyId) {
      loadDocuments(companyId)
    } else {
      setDocuments([])
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
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">
                  Knowledge Documents
                </Typography>
                {documents.length > 0 && (
                  <Box display="flex" alignItems="center" gap={1}>
                    <Button
                      size="small"
                      startIcon={<SelectAll />}
                      onClick={handleSelectAll}
                    >
                      {selectedDocuments.size === documents.length ? 'Deselect All' : 'Select All'}
                    </Button>
                    {selectedDocuments.size > 0 && (
                      <Button
                        size="small"
                        color="error"
                        startIcon={<DeleteSweepRounded />}
                        onClick={() => setBulkDeleteDialogOpen(true)}
                      >
                        Delete Selected ({selectedDocuments.size})
                      </Button>
                    )}
                  </Box>
                )}
              </Box>
              
              {selectedDocuments.size > 0 && (
                <Toolbar
                  sx={{
                    pl: { sm: 2 },
                    pr: { xs: 1, sm: 1 },
                    bgcolor: 'action.selected',
                    borderRadius: 1,
                    mb: 2
                  }}
                >
                  <Typography
                    sx={{ flex: '1 1 100%' }}
                    color="inherit"
                    variant="subtitle1"
                  >
                    {selectedDocuments.size} document(s) selected
                  </Typography>
                </Toolbar>
              )}
              
              {loading ? (
                <Box display="flex" justifyContent="center" py={4}>
                  <LinearProgress sx={{ width: '50%' }} />
                </Box>
              ) : documents.length === 0 ? (
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
                      <ListItemIcon>
                        <Checkbox
                          edge="start"
                          checked={selectedDocuments.has(document.id)}
                          onChange={() => handleDocumentSelect(document.id)}
                        />
                      </ListItemIcon>
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

      {/* Bulk Delete Confirmation Dialog */}
      <Dialog
        open={bulkDeleteDialogOpen}
        onClose={() => setBulkDeleteDialogOpen(false)}
      >
        <DialogTitle>Confirm Bulk Delete</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete {selectedDocuments.size} document(s)? 
            This action cannot be undone and will remove all associated chunks and embeddings.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setBulkDeleteDialogOpen(false)}>
            Cancel
          </Button>
          <Button
            onClick={handleBulkDelete}
            color="error"
            variant="contained"
          >
            Delete {selectedDocuments.size} Documents
          </Button>
        </DialogActions>
      </Dialog>

      {/* Success Message Snackbar */}
      <Snackbar
        open={!!successMessage}
        autoHideDuration={6000}
        onClose={() => setSuccessMessage('')}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          onClose={() => setSuccessMessage('')}
          severity="success"
          variant="filled"
          sx={{ width: '100%' }}
        >
          {successMessage}
        </Alert>
      </Snackbar>
    </Box>
  )
}

export default KnowledgeManagementPage
