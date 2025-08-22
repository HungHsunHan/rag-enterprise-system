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
  Chip,
  IconButton,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  Card,
  CardContent,
  Pagination,
  InputAdornment,
  Alert,
  CircularProgress
} from '@mui/material'
import {
  Search,
  ThumbUp,
  ThumbDown,
  TrendingUp,
  TrendingDown,
  Assessment
} from '@mui/icons-material'
import { apiClient } from '../../api/client'

interface Feedback {
  id: string
  user_id: string | null
  question: string
  answer: string
  feedback: 'POSITIVE' | 'NEGATIVE'
  created_at: string
}

interface FeedbackStats {
  total_count: number
  positive_count: number
  negative_count: number
  positive_percentage: number
}

const FeedbackDashboard: React.FC = () => {
  const [feedbackList, setFeedbackList] = useState<Feedback[]>([])
  const [stats, setStats] = useState<FeedbackStats>({
    total_count: 0,
    positive_count: 0,
    negative_count: 0,
    positive_percentage: 0
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [searchTerm, setSearchTerm] = useState('')
  const [feedbackFilter, setFeedbackFilter] = useState<string>('all')
  const [selectedCompanyId, setSelectedCompanyId] = useState<string>('')
  
  const itemsPerPage = 20

  // Mock company data - in real app, this would come from API
  const companies = [
    { id: '1', name: 'Tech Corp' },
    { id: '2', name: 'Finance Ltd' },
    { id: '3', name: 'Healthcare Inc' }
  ]

  const loadFeedbackData = async () => {
    if (!selectedCompanyId) return
    
    setLoading(true)
    setError(null)
    
    try {
      // Load feedback list
      const params = new URLSearchParams({
        company_id: selectedCompanyId,
        limit: itemsPerPage.toString(),
        offset: ((page - 1) * itemsPerPage).toString()
      })
      
      if (feedbackFilter !== 'all') {
        params.append('feedback_type', feedbackFilter.toUpperCase())
      }
      
      const feedbackResponse = await apiClient.get(`/api/admin/feedback?${params}`)
      setFeedbackList(feedbackResponse.data)
      
      // Load stats
      const statsResponse = await apiClient.get(`/api/admin/feedback/stats?company_id=${selectedCompanyId}`)
      setStats(statsResponse.data)
      
    } catch (error) {
      console.error('Error loading feedback data:', error)
      setError('Failed to load feedback data. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const searchFeedback = async () => {
    if (!selectedCompanyId || !searchTerm.trim()) {
      loadFeedbackData()
      return
    }
    
    setLoading(true)
    setError(null)
    
    try {
      const params = new URLSearchParams({
        company_id: selectedCompanyId,
        search_term: searchTerm,
        limit: itemsPerPage.toString(),
        offset: ((page - 1) * itemsPerPage).toString()
      })
      
      const response = await apiClient.get(`/api/admin/feedback/search?${params}`)
      setFeedbackList(response.data)
      
    } catch (error) {
      console.error('Error searching feedback:', error)
      setError('Failed to search feedback. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (selectedCompanyId) {
      if (searchTerm.trim()) {
        const timeoutId = setTimeout(searchFeedback, 300)
        return () => clearTimeout(timeoutId)
      } else {
        loadFeedbackData()
      }
    }
  }, [selectedCompanyId, page, feedbackFilter, searchTerm])

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  const truncateText = (text: string, maxLength: number = 100) => {
    return text.length > maxLength ? `${text.substring(0, maxLength)}...` : text
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Feedback Dashboard
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
          {/* Statistics Cards */}
          <Grid container spacing={3} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Assessment color="primary" />
                    <Box>
                      <Typography variant="h6">{stats.total_count}</Typography>
                      <Typography variant="body2" color="text.secondary">
                        Total Feedback
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <ThumbUp color="success" />
                    <Box>
                      <Typography variant="h6">{stats.positive_count}</Typography>
                      <Typography variant="body2" color="text.secondary">
                        Positive
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <ThumbDown color="error" />
                    <Box>
                      <Typography variant="h6">{stats.negative_count}</Typography>
                      <Typography variant="body2" color="text.secondary">
                        Negative
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {stats.positive_percentage >= 70 ? (
                      <TrendingUp color="success" />
                    ) : (
                      <TrendingDown color="error" />
                    )}
                    <Box>
                      <Typography variant="h6">{stats.positive_percentage.toFixed(1)}%</Typography>
                      <Typography variant="body2" color="text.secondary">
                        Satisfaction
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Filters and Search */}
          <Box sx={{ mb: 3, display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
            <TextField
              placeholder="Search questions or answers..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
              }}
              sx={{ minWidth: 300 }}
            />
            
            <FormControl sx={{ minWidth: 150 }}>
              <InputLabel>Filter</InputLabel>
              <Select
                value={feedbackFilter}
                onChange={(e) => setFeedbackFilter(e.target.value)}
                label="Filter"
              >
                <MenuItem value="all">All Feedback</MenuItem>
                <MenuItem value="positive">Positive Only</MenuItem>
                <MenuItem value="negative">Negative Only</MenuItem>
              </Select>
            </FormControl>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {/* Feedback Table */}
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
                      <TableCell>Date</TableCell>
                      <TableCell>Question</TableCell>
                      <TableCell>Answer</TableCell>
                      <TableCell>Feedback</TableCell>
                      <TableCell>User ID</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {feedbackList.map((feedback) => (
                      <TableRow key={feedback.id}>
                        <TableCell>
                          <Typography variant="body2">
                            {formatDate(feedback.created_at)}
                          </Typography>
                        </TableCell>
                        <TableCell sx={{ maxWidth: 200 }}>
                          <Typography variant="body2" title={feedback.question}>
                            {truncateText(feedback.question)}
                          </Typography>
                        </TableCell>
                        <TableCell sx={{ maxWidth: 300 }}>
                          <Typography variant="body2" title={feedback.answer}>
                            {truncateText(feedback.answer, 150)}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={feedback.feedback === 'POSITIVE' ? 'Positive' : 'Negative'}
                            color={feedback.feedback === 'POSITIVE' ? 'success' : 'error'}
                            size="small"
                            icon={feedback.feedback === 'POSITIVE' ? <ThumbUp /> : <ThumbDown />}
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" color="text.secondary">
                            {feedback.user_id || 'Anonymous'}
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
                
                {feedbackList.length === 0 && !loading && (
                  <Box sx={{ p: 4, textAlign: 'center' }}>
                    <Typography variant="body1" color="text.secondary">
                      {searchTerm ? 'No feedback found matching your search.' : 'No feedback data available.'}
                    </Typography>
                  </Box>
                )}
              </TableContainer>
            )}
          </Paper>

          {/* Pagination */}
          {feedbackList.length > 0 && (
            <Box sx={{ display: 'flex', justifyContent: 'center' }}>
              <Pagination
                count={Math.ceil(stats.total_count / itemsPerPage)}
                page={page}
                onChange={(_, newPage) => setPage(newPage)}
                color="primary"
              />
            </Box>
          )}
        </>
      )}
    </Box>
  )
}

export default FeedbackDashboard