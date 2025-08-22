import React, { useState, useEffect } from 'react'
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Pagination,
  InputAdornment,
  Alert,
  CircularProgress,
  Card,
  CardContent,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button
} from '@mui/material'
import {
  Search,
  Article,
  Storage,
  Visibility
} from '@mui/icons-material'
import { apiClient } from '../../api/client'

interface DocumentChunk {
  id: string
  document_id: string
  chunk_text: string
  chunk_index: number
  created_at: string
}

interface ChunksResponse {
  chunks: DocumentChunk[]
}

const KnowledgeChunksPage: React.FC = () => {
  const [chunks, setChunks] = useState<DocumentChunk[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCompanyId, setSelectedCompanyId] = useState<string>('')
  const [selectedChunk, setSelectedChunk] = useState<DocumentChunk | null>(null)
  const [viewDialogOpen, setViewDialogOpen] = useState(false)
  const [totalChunks, setTotalChunks] = useState(0)
  
  const itemsPerPage = 20

  // Mock company data - in real app, this would come from API
  const companies = [
    { id: '1', name: 'Tech Corp' },
    { id: '2', name: 'Finance Ltd' },
    { id: '3', name: 'Healthcare Inc' }
  ]

  const loadChunks = async () => {
    if (!selectedCompanyId) return
    
    setLoading(true)
    setError(null)
    
    try {
      const params = new URLSearchParams({
        company_id: selectedCompanyId,
        limit: itemsPerPage.toString(),
        offset: ((page - 1) * itemsPerPage).toString()
      })
      
      const response = await apiClient.get<ChunksResponse>(`/api/admin/knowledge/chunks?${params}`)
      setChunks(response.data.chunks)
      setTotalChunks(response.data.chunks.length) // This should come from a total count in the API
      
    } catch (error) {
      console.error('Error loading chunks:', error)
      setError('Failed to load knowledge chunks. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const searchChunks = async () => {
    if (!selectedCompanyId) return
    
    setLoading(true)
    setError(null)
    
    try {
      const searchParams = new URLSearchParams({
        company_id: selectedCompanyId,
        limit: itemsPerPage.toString(),
        offset: ((page - 1) * itemsPerPage).toString()
      })
      
      // Note: This is a simplified search - in a real implementation,
      // you would have a dedicated search endpoint for chunks
      const response = await apiClient.get<ChunksResponse>(`/api/admin/knowledge/chunks?${searchParams}`)
      
      // Filter results client-side for demo (should be done server-side in production)
      const filteredChunks = searchTerm.trim() 
        ? response.data.chunks.filter(chunk => 
            chunk.chunk_text.toLowerCase().includes(searchTerm.toLowerCase())
          )
        : response.data.chunks
      
      setChunks(filteredChunks)
      setTotalChunks(filteredChunks.length)
      
    } catch (error) {
      console.error('Error searching chunks:', error)
      setError('Failed to search knowledge chunks. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (selectedCompanyId) {
      if (searchTerm.trim()) {
        const timeoutId = setTimeout(searchChunks, 300)
        return () => clearTimeout(timeoutId)
      } else {
        loadChunks()
      }
    }
  }, [selectedCompanyId, page, searchTerm])

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString()
  }

  const truncateText = (text: string, maxLength: number = 100) => {
    return text.length > maxLength ? `${text.substring(0, maxLength)}...` : text
  }

  const handleViewChunk = (chunk: DocumentChunk) => {
    setSelectedChunk(chunk)
    setViewDialogOpen(true)
  }

  const handleCloseDialog = () => {
    setViewDialogOpen(false)
    setSelectedChunk(null)
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Knowledge Base Chunks
      </Typography>
      
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        View and search through document chunks in the knowledge base to understand how content is processed and stored.
      </Typography>
      
      {/* Company Selection */}
      <Box sx={{ mb: 3 }}>
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel>Select Company</InputLabel>
          <Select
            value={selectedCompanyId}
            onChange={(e) => setSelectedCompanyId(e.target.value)}
            label="Select Company"
          >
            {companies.map((company) => (
              <MenuItem key={company.id} value={company.id}>
                {company.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

      {selectedCompanyId && (
        <>
          {/* Statistics Card */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Storage color="primary" />
                <Box>
                  <Typography variant="h6">Knowledge Base Overview</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total chunks processed: {totalChunks} | 
                    Showing {chunks.length} chunks on page {page}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>

          {/* Search */}
          <Box sx={{ mb: 3 }}>
            <TextField
              fullWidth
              placeholder="Search knowledge chunks..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
              }}
              sx={{ maxWidth: 500 }}
            />
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {/* Chunks Table */}
          <Paper sx={{ mb: 3 }}>
            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                <CircularProgress />
              </Box>
            ) : (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Chunk Index</TableCell>
                      <TableCell>Content Preview</TableCell>
                      <TableCell>Document ID</TableCell>
                      <TableCell>Created Date</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {chunks.map((chunk) => (
                      <TableRow key={chunk.id}>
                        <TableCell>
                          <Chip 
                            label={`#${chunk.chunk_index}`} 
                            size="small" 
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell sx={{ maxWidth: 400 }}>
                          <Typography variant="body2" title={chunk.chunk_text}>
                            {truncateText(chunk.chunk_text, 200)}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" color="text.secondary" sx={{ fontFamily: 'monospace' }}>
                            {chunk.document_id.substring(0, 8)}...
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {formatDate(chunk.created_at)}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Button
                            size="small"
                            startIcon={<Visibility />}
                            onClick={() => handleViewChunk(chunk)}
                          >
                            View
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
                
                {chunks.length === 0 && !loading && (
                  <Box sx={{ p: 4, textAlign: 'center' }}>
                    <Article sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                    <Typography variant="h6" color="text.secondary" gutterBottom>
                      No Knowledge Chunks Found
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {searchTerm 
                        ? 'No chunks match your search criteria. Try a different search term.' 
                        : 'No document chunks have been processed yet. Upload some documents to see them here.'
                      }
                    </Typography>
                  </Box>
                )}
              </TableContainer>
            )}
          </Paper>

          {/* Pagination */}
          {chunks.length > 0 && (
            <Box sx={{ display: 'flex', justifyContent: 'center' }}>
              <Pagination
                count={Math.ceil(totalChunks / itemsPerPage)}
                page={page}
                onChange={(_, newPage) => setPage(newPage)}
                color="primary"
              />
            </Box>
          )}
        </>
      )}

      {/* View Chunk Dialog */}
      <Dialog 
        open={viewDialogOpen} 
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Article />
            Chunk #{selectedChunk?.chunk_index} Details
          </Box>
        </DialogTitle>
        <DialogContent>
          {selectedChunk && (
            <Box sx={{ mt: 1 }}>
              <Typography variant="subtitle2" gutterBottom>
                Document ID:
              </Typography>
              <Typography variant="body2" sx={{ fontFamily: 'monospace', mb: 2 }}>
                {selectedChunk.document_id}
              </Typography>
              
              <Typography variant="subtitle2" gutterBottom>
                Created Date:
              </Typography>
              <Typography variant="body2" sx={{ mb: 2 }}>
                {new Date(selectedChunk.created_at).toLocaleString()}
              </Typography>
              
              <Typography variant="subtitle2" gutterBottom>
                Content:
              </Typography>
              <Paper sx={{ p: 2, backgroundColor: 'grey.50' }}>
                <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                  {selectedChunk.chunk_text}
                </Typography>
              </Paper>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default KnowledgeChunksPage