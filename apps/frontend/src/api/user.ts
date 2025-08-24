import { apiClient } from './client'
import { useAuthStore } from '../store/authStore'

export interface QuestionRequest {
  question: string
}

export interface AnswerResponse {
  answer: string
}

export interface FeedbackRequest {
  question: string
  answer: string
  feedback: 'POSITIVE' | 'NEGATIVE'
}

class UserApi {
  // Chat functionality
  async askQuestion(questionData: QuestionRequest): Promise<AnswerResponse> {
    const response = await apiClient.post('/api/v1/chat', questionData)
    return response.data
  }

  // Streaming chat functionality
  async askQuestionStream(
    questionData: QuestionRequest,
    onToken: (token: string) => void,
    onComplete: () => void,
    onError: (error: string) => void
  ): Promise<void> {
    try {
      const token = useAuthStore.getState().token
      if (!token) {
        throw new Error('No authentication token found')
      }

      const response = await fetch('/api/v1/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(questionData),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body?.getReader()
      if (!reader) {
        throw new Error('Failed to get response reader')
      }

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || '' // Keep the last incomplete line in buffer

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              if (data.done) {
                onComplete()
                return
              } else if (data.token) {
                onToken(data.token)
              }
            } catch (e) {
              console.error('Failed to parse SSE data:', e)
            }
          }
        }
      }

      onComplete()
    } catch (error) {
      console.error('Streaming error:', error)
      onError(error instanceof Error ? error.message : 'Unknown streaming error')
    }
  }

  async submitFeedback(feedbackData: FeedbackRequest): Promise<{ message: string }> {
    const response = await apiClient.post('/api/v1/chat/feedback', feedbackData)
    return response.data
  }
}

export const userApi = new UserApi()
export default userApi