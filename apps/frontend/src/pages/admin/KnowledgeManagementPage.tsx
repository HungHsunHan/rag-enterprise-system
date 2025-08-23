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
  Snackbar,
  TextField,
  Stack,
  Divider
} from '@mui/material'
import {
  UploadFileRounded,
  DeleteRounded,
  FolderRounded,
  DescriptionRounded,
  DeleteSweepRounded,
  SelectAll,
  SettingsRounded,
  PlayArrowRounded
} from '@mui/icons-material'
import { adminApi } from '../../api/admin'
import type { Company, KnowledgeDocument, DocumentProcessRequest } from '../../api/admin'

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
  const [uploadQueue, setUploadQueue] = useState<File[]>([])
  const [uploadProgress, setUploadProgress] = useState<{total: number, completed: number, current: string}>({total: 0, completed: 0, current: ''})
  const [processDialogOpen, setProcessDialogOpen] = useState(false)
  const [processingDocuments, setProcessingDocuments] = useState<Set<string>>(new Set())
  const [documentProgress, setDocumentProgress] = useState<Map<string, number>>(new Map())
  const [chunkSize, setChunkSize] = useState(1000)
  const [overlapLength, setOverlapLength] = useState(200)
  
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
    
    // Clear any existing error
    setError('')
    
    // Try to trigger the file input click
    const fileInput = fileInputRef.current
    if (fileInput) {
      try {
        // Small delay to ensure the element is fully rendered and accessible
        setTimeout(() => {
          fileInput.click()
        }, 10)
      } catch (err) {
        console.error('Failed to trigger file input:', err)
        setError('Failed to open file dialog. Please try refreshing the page.')
      }
    } else {
      console.error('File input ref not found')
      setError('File input not found. Please refresh the page.')
    }
  }

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || [])
    if (files.length === 0) return

    // Set up upload progress tracking
    setUploading(true)
    setError('')
    setUploadQueue(files)
    setUploadProgress({ total: files.length, completed: 0, current: '' })

    try {
      // Upload files sequentially with progress tracking
      for (let i = 0; i < files.length; i++) {
        const file = files[i]
        setUploadProgress(prev => ({ ...prev, current: file.name }))
        
        try {
          await adminApi.uploadDocument(selectedCompany, file)
          setUploadProgress(prev => ({ ...prev, completed: prev.completed + 1 }))
        } catch (fileError: any) {
          setError(prev => prev ? `${prev}, Failed to upload ${file.name}` : `Failed to upload ${file.name}`)
        }
      }
      
      // Refresh documents list
      await loadDocuments(selectedCompany)
      
      if (uploadProgress.completed === files.length) {
        setSuccessMessage(`Successfully uploaded ${files.length} file(s)`)
      }
      
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload documents')
    } finally {
      setUploading(false)
      setUploadQueue([])
      setUploadProgress({ total: 0, completed: 0, current: '' })
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
      case 'PENDING': return 'info'
      default: return 'default'
    }
  }

  const handleProcessDocuments = () => {
    if (selectedDocuments.size === 0) {
      setError('Please select documents to process')
      return
    }
    setProcessDialogOpen(true)
  }

  const confirmProcessDocuments = async () => {
    if (selectedDocuments.size === 0) return

    setProcessDialogOpen(false)
    const docIds = Array.from(selectedDocuments)
    setProcessingDocuments(new Set(docIds))
    
    const processParams: DocumentProcessRequest = {
      chunk_size: chunkSize,
      overlap_length: overlapLength
    }

    // Process each document
    for (const documentId of docIds) {
      try {
        setDocumentProgress(prev => new Map(prev.set(documentId, 0)))
        
        await adminApi.processDocument(documentId, processParams)
        
        // Start progress tracking for this document
        trackDocumentProgress(documentId)
        
      } catch (err: any) {
        setError(err.response?.data?.detail || `Failed to process document ${documentId}`)
        setProcessingDocuments(prev => {
          const newSet = new Set(prev)
          newSet.delete(documentId)
          return newSet
        })
      }
    }
    
    setSelectedDocuments(new Set())
  }

  const trackDocumentProgress = async (documentId: string) => {
    const checkProgress = async () => {
      try {
        const status = await adminApi.getDocumentProcessingStatus(documentId)
        
        if (status.status === 'COMPLETED') {
          setDocumentProgress(prev => new Map(prev.set(documentId, 100)))
          setProcessingDocuments(prev => {
            const newSet = new Set(prev)
            newSet.delete(documentId)
            return newSet
          })
          // Refresh documents list
          if (selectedCompany) {
            await loadDocuments(selectedCompany)
          }
          return
        } else if (status.status === 'FAILED') {
          setError(`Document processing failed: ${documentId}`)
          setProcessingDocuments(prev => {
            const newSet = new Set(prev)
            newSet.delete(documentId)
            return newSet
          })
          return
        } else if (status.status === 'PROCESSING') {
          // Simulate progress based on time (since we don't have real-time progress)
          setDocumentProgress(prev => {
            const currentProgress = prev.get(documentId) || 0
            const newProgress = Math.min(90, currentProgress + 10)
            return new Map(prev.set(documentId, newProgress))
          })
        }
        
        // Continue checking after 2 seconds
        setTimeout(checkProgress, 2000)
      } catch (err) {
        console.error('Failed to check document progress:', err)
        setProcessingDocuments(prev => {
          const newSet = new Set(prev)
          newSet.delete(documentId)
          return newSet
        })
      }
    }
    
    checkProgress()
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
                  Upload Files
                </Button>
              </Box>
              
              {uploading && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {uploadProgress.total > 1 ? (
                      <>
                        Uploading files: {uploadProgress.completed}/{uploadProgress.total} completed
                        {uploadProgress.current && (
                          <Typography component="span" variant="caption" display="block" sx={{ mt: 0.5 }}>
                            Current: {uploadProgress.current}
                          </Typography>
                        )}
                      </>
                    ) : (
                      `Uploading and processing document...`
                    )}
                  </Typography>
                  <LinearProgress 
                    variant={uploadProgress.total > 1 ? "determinate" : "indeterminate"}
                    value={uploadProgress.total > 1 ? (uploadProgress.completed / uploadProgress.total) * 100 : undefined}
                  />
                  {uploadProgress.total > 1 && (
                    <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
                      {Math.round((uploadProgress.completed / uploadProgress.total) * 100)}% complete
                    </Typography>
                  )}
                </Box>
              )}

              <Typography variant="body2" color="text.secondary">
                Supported formats: PDF, DOCX, TXT (max 10MB each file, multiple files supported)
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
                      <>
                        <Button
                          size="small"
                          variant="outlined"
                          startIcon={<SettingsRounded />}
                          onClick={handleProcessDocuments}
                        >
                          Process Selected ({selectedDocuments.size})
                        </Button>
                        <Button
                          size="small"
                          color="error"
                          startIcon={<DeleteSweepRounded />}
                          onClick={() => setBulkDeleteDialogOpen(true)}
                        >
                          Delete Selected ({selectedDocuments.size})
                        </Button>
                      </>
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
                        secondary={
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              Uploaded: {new Date(document.uploaded_at).toLocaleDateString()}
                            </Typography>
                            {processingDocuments.has(document.id) && (
                              <Box sx={{ mt: 1 }}>
                                <Typography variant="caption" color="text.secondary">
                                  Processing... {documentProgress.get(document.id) || 0}%
                                </Typography>
                                <LinearProgress 
                                  variant="determinate" 
                                  value={documentProgress.get(document.id) || 0}
                                  sx={{ mt: 0.5 }}
                                />
                              </Box>
                            )}
                          </Box>
                        }
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
        multiple
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

      <Dialog
        open={processDialogOpen}
        onClose={() => setProcessDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={1}>
            <SettingsRounded />
            Process Documents
          </Box>
        </DialogTitle>
        <DialogContent>
          <Stack spacing={3} sx={{ mt: 1 }}>
            <Typography variant="body2" color="text.secondary">
              Configure processing parameters for {selectedDocuments.size} selected document(s).
              This will create text chunks with embeddings for RAG functionality.
            </Typography>
            
            <Divider />
            
            <TextField
              label="Chunk Size"
              type="number"
              value={chunkSize}
              onChange={(e) => setChunkSize(parseInt(e.target.value) || 1000)}
              helperText="Number of characters per text chunk (recommended: 500-2000)"
              inputProps={{ min: 100, max: 4000, step: 100 }}
              fullWidth
            />
            
            <TextField
              label="Overlap Length"
              type="number"
              value={overlapLength}
              onChange={(e) => setOverlapLength(parseInt(e.target.value) || 200)}
              helperText="Character overlap between chunks (recommended: 10-20% of chunk size)"
              inputProps={{ min: 0, max: Math.floor(chunkSize * 0.5), step: 50 }}
              fullWidth
            />
            
            <Box sx={{ p: 2, bgcolor: 'info.light', borderRadius: 1 }}>
              <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                Estimated chunks: ~{Math.ceil(selectedDocuments.size * 10)} per document
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Processing time varies based on document size and content complexity.
              </Typography>
            </Box>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setProcessDialogOpen(false)}>
            Cancel
          </Button>
          <Button
            onClick={confirmProcessDocuments}
            variant="contained"
            startIcon={<PlayArrowRounded />}
          >
            Start Processing
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
