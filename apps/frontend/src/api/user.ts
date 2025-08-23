import { apiClient } from './client'

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

  async submitFeedback(feedbackData: FeedbackRequest): Promise<{ message: string }> {
    const response = await apiClient.post('/api/v1/chat/feedback', feedbackData)
    return response.data
  }
}

export const userApi = new UserApi()
export default userApi