import apiClient from './client'

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
    const response = await apiClient.post('/api/v1/admin/login', data)
    return response.data
  },

  userLogin: async (data: UserLoginRequest): Promise<AuthResponse> => {
    const response = await apiClient.post('/api/v1/login', data)
    return response.data
  },
}