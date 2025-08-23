import apiClient from './client'
import { mockLogin } from './mock-auth'

export interface AdminLoginRequest {
  email: string
  password: string
}

export interface UserLoginRequest {
  employee_id: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
}

export const authApi = {
  adminLogin: async (data: AdminLoginRequest): Promise<AuthResponse> => {
    try {
      const response = await apiClient.post('/api/v1/admin/login', data)
      return response.data
    } catch (error) {
      if (import.meta.env.DEV) {
        console.warn('Backend unavailable, using mock authentication in DEV mode', error)
        return await mockLogin.admin(data.email, data.password)
      }
      throw error
    }
  },

  userLogin: async (data: UserLoginRequest): Promise<AuthResponse> => {
    try {
      const response = await apiClient.post('/api/v1/login', data)
      return response.data
    } catch (error) {
      if (import.meta.env.DEV) {
        console.warn('Backend unavailable, using mock authentication in DEV mode', error)
        return await mockLogin.user(data.employee_id)
      }
      throw error
    }
  },
}
