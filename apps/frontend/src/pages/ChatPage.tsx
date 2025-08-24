import React, { useState } from 'react'
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Typography,
  List,
  ListItem,
  Avatar,
  Chip,
  CircularProgress,
  Snackbar,
  Alert
} from '@mui/material'
import { SendRounded, ThumbUpRounded, ThumbDownRounded } from '@mui/icons-material'
import { userApi } from '../api/user'

interface Message {
  id: string
  type: 'user' | 'assistant'
  content: string
  timestamp: Date
  feedback?: 'positive' | 'negative'
  feedbackSubmitted?: boolean
  feedbackLoading?: boolean
}


interface FeedbackNotification {
  open: boolean
  message: string
  severity: 'success' | 'error'
}

const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'assistant',
      content: 'Hello! I\'m your HR assistant. I can help you with company policies, procedures, and answer questions based on your company\'s knowledge base. What would you like to know?',
      timestamp: new Date()
    }
  ])
  const [inputMessage, setInputMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [feedbackNotification, setFeedbackNotification] = useState<FeedbackNotification>({
    open: false,
    message: '',
    severity: 'success'
  })

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    }

    const assistantMessageId = (Date.now() + 1).toString()
    const initialAssistantMessage: Message = {
      id: assistantMessageId,
      type: 'assistant',
      content: '',
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage, initialAssistantMessage])
    setInputMessage('')
    setLoading(true)

    try {
      let assistantContent = ''
      
      await userApi.askQuestionStream(
        { question: inputMessage },
        // On token received
        (token: string) => {
          assistantContent += token
          setMessages(prev => 
            prev.map(msg => 
              msg.id === assistantMessageId 
                ? { ...msg, content: assistantContent }
                : msg
            )
          )
        },
        // On completion
        () => {
          setLoading(false)
        },
        // On error
        (error: string) => {
          console.error('Streaming error:', error)
          setMessages(prev => 
            prev.map(msg => 
              msg.id === assistantMessageId 
                ? { ...msg, content: 'Sorry, I encountered an error while processing your question. Please try again.' }
                : msg
            )
          )
          setLoading(false)
        }
      )
    } catch (error) {
      console.error('Error in handleSendMessage:', error)
      setMessages(prev => 
        prev.map(msg => 
          msg.id === assistantMessageId 
            ? { ...msg, content: 'Sorry, I encountered an error while processing your question. Please try again.' }
            : msg
        )
      )
      setLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const handleFeedback = async (messageId: string, feedback: 'positive' | 'negative') => {
    // Find the current message and the previous user message
    const messageIndex = messages.findIndex(m => m.id === messageId)
    const currentMessage = messages[messageIndex]
    
    if (!currentMessage || currentMessage.type !== 'assistant') {
      console.error('Invalid message for feedback')
      return
    }

    // Find the previous user message
    let userQuestion = ''
    for (let i = messageIndex - 1; i >= 0; i--) {
      if (messages[i].type === 'user') {
        userQuestion = messages[i].content
        break
      }
    }

    // Set loading state for this specific message
    setMessages(prev =>
      prev.map(msg =>
        msg.id === messageId 
          ? { ...msg, feedback, feedbackLoading: true } 
          : msg
      )
    )

    try {
      // Submit feedback to API
      await userApi.submitFeedback({
        question: userQuestion,
        answer: currentMessage.content,
        feedback: feedback.toUpperCase() as 'POSITIVE' | 'NEGATIVE'
      })

      // Update message state on success
      setMessages(prev =>
        prev.map(msg =>
          msg.id === messageId 
            ? { ...msg, feedbackSubmitted: true, feedbackLoading: false } 
            : msg
        )
      )

      // Show success notification
      setFeedbackNotification({
        open: true,
        message: 'Thank you for your feedback!',
        severity: 'success'
      })

    } catch (error) {
      console.error('Failed to submit feedback:', error)
      
      // Reset feedback state on error
      setMessages(prev =>
        prev.map(msg =>
          msg.id === messageId 
            ? { ...msg, feedback: undefined, feedbackLoading: false } 
            : msg
        )
      )

      // Show error notification
      setFeedbackNotification({
        open: true,
        message: 'Failed to submit feedback. Please try again.',
        severity: 'error'
      })
    }
  }

  const handleCloseNotification = () => {
    setFeedbackNotification({ ...feedbackNotification, open: false })
  }

  return (
    <Box sx={{ height: 'calc(100vh - 140px)', display: 'flex', flexDirection: 'column' }}>
      <Typography variant="h4" gutterBottom>
        HR Assistant
      </Typography>
      
      {/* Messages Area */}
      <Paper 
        sx={{ 
          flex: 1, 
          p: 2, 
          mb: 2, 
          overflow: 'auto',
          display: 'flex',
          flexDirection: 'column'
        }}
      >
        <List sx={{ flex: 1 }}>
          {messages.map((message) => (
            <ListItem
              key={message.id}
              sx={{
                flexDirection: 'column',
                alignItems: message.type === 'user' ? 'flex-end' : 'flex-start',
                pb: 2
              }}
            >
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: 1,
                  maxWidth: '80%',
                  flexDirection: message.type === 'user' ? 'row-reverse' : 'row'
                }}
              >
                <Avatar
                  sx={{
                    bgcolor: message.type === 'user' ? 'primary.main' : 'secondary.main',
                    width: 32,
                    height: 32
                  }}
                >
                  {message.type === 'user' ? 'U' : 'A'}
                </Avatar>
                
                <Box>
                  <Paper
                    sx={{
                      p: 2,
                      bgcolor: message.type === 'user' ? 'primary.light' : 'grey.100',
                      color: message.type === 'user' ? 'white' : 'text.primary'
                    }}
                  >
                    {message.type === 'assistant' && !message.content && loading ? (
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <CircularProgress size={16} />
                        <Typography variant="body2" color="text.secondary">
                          Thinking...
                        </Typography>
                      </Box>
                    ) : (
                      <Typography variant="body1">{message.content}</Typography>
                    )}
                  </Paper>
                  
                  {message.type === 'assistant' && (
                    <Box sx={{ mt: 1, display: 'flex', gap: 1, alignItems: 'center' }}>
                      <Typography variant="caption" color="text.secondary">
                        Was this helpful?
                      </Typography>
                      
                      {message.feedbackLoading ? (
                        <CircularProgress size={16} sx={{ ml: 1 }} />
                      ) : (
                        <>
                          <IconButton
                            size="small"
                            onClick={() => handleFeedback(message.id, 'positive')}
                            disabled={message.feedbackSubmitted || message.feedbackLoading}
                            color={message.feedback === 'positive' ? 'primary' : 'default'}
                            sx={{
                              opacity: message.feedbackSubmitted && message.feedback !== 'positive' ? 0.5 : 1
                            }}
                          >
                            <ThumbUpRounded fontSize="small" />
                          </IconButton>
                          <IconButton
                            size="small"
                            onClick={() => handleFeedback(message.id, 'negative')}
                            disabled={message.feedbackSubmitted || message.feedbackLoading}
                            color={message.feedback === 'negative' ? 'error' : 'default'}
                            sx={{
                              opacity: message.feedbackSubmitted && message.feedback !== 'negative' ? 0.5 : 1
                            }}
                          >
                            <ThumbDownRounded fontSize="small" />
                          </IconButton>
                        </>
                      )}
                      
                      {message.feedback && message.feedbackSubmitted && (
                        <Chip
                          label={message.feedback === 'positive' ? 'Marked as helpful' : 'Marked as not helpful'}
                          size="small"
                          color={message.feedback === 'positive' ? 'success' : 'error'}
                          variant="filled"
                        />
                      )}
                    </Box>
                  )}
                </Box>
              </Box>
            </ListItem>
          ))}
          
        </List>
      </Paper>
      
      {/* Input Area */}
      <Paper sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            fullWidth
            multiline
            maxRows={4}
            placeholder="Ask me anything about company policies..."
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={loading}
          />
          <IconButton
            color="primary"
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || loading}
          >
            <SendRounded />
          </IconButton>
        </Box>
      </Paper>
      
      {/* Feedback Notification */}
      <Snackbar
        open={feedbackNotification.open}
        autoHideDuration={3000}
        onClose={handleCloseNotification}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          onClose={handleCloseNotification}
          severity={feedbackNotification.severity}
          variant="filled"
          sx={{ width: '100%' }}
        >
          {feedbackNotification.message}
        </Alert>
      </Snackbar>
    </Box>
  )
}

export default ChatPage