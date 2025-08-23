import { apiClient } from './client'

export interface Company {
  id: string
  name: string
  created_at: string
}

export interface CompanyCreate {
  name: string
}

export interface KnowledgeDocument {
  id: string
  file_name: string
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED'
  company_id: string
  uploaded_at: string
}

export interface DocumentChunk {
  id: string
  document_id: string
  chunk_text: string
  chunk_index: number
  created_at: string
}

export interface DocumentProcessRequest {
  chunk_size: number
  overlap_length: number
}

export interface DocumentProcessingStatus {
  document_id: string
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED'
  chunk_size?: number
  overlap_length?: number
  chunks_count: number
  uploaded_at: string
  is_shared: boolean
}

export interface FeedbackStats {
  total_count: number
  positive_count: number
  negative_count: number
  positive_percentage: number
}

export interface FeedbackResponse {
  id: string
  user_id?: string
  question: string
  answer: string
  feedback: string
  created_at: string
}

export interface CompanyMetrics {
  company_id: string
  company_name: string
  user_count: number
  document_count: number
  queries_today: number
}

export interface DashboardMetrics {
  total_companies: number
  shared_documents_count: number
  company_metrics: CompanyMetrics[]
  timestamp: string
}

export interface SystemSummary {
  total_users: number
  total_documents: number
  total_queries_today: number
  total_companies: number
}

class AdminApi {
  // Company Management
  async getCompanies(): Promise<Company[]> {
    const response = await apiClient.get('/api/v1/admin/companies')
    return response.data
  }

  async createCompany(companyData: CompanyCreate): Promise<Company> {
    const response = await apiClient.post('/api/v1/admin/companies', companyData)
    return response.data
  }

  async deleteCompany(companyId: string): Promise<{ message: string }> {
    const response = await apiClient.delete(`/api/v1/admin/companies/${companyId}`)
    return response.data
  }

  // Document Management
  async getDocuments(companyId: string): Promise<KnowledgeDocument[]> {
    const response = await apiClient.get(`/api/v1/admin/knowledge/documents?company_id=${companyId}`)
    return response.data
  }

  async uploadDocument(companyId: string, file: File): Promise<{ message: string; document_id: string }> {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await apiClient.post(
      `/api/v1/admin/knowledge/documents?company_id=${companyId}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return response.data
  }

  async deleteDocument(documentId: string): Promise<{ message: string }> {
    const response = await apiClient.delete(`/api/v1/admin/knowledge/documents/${documentId}`)
    return response.data
  }

  async bulkDeleteDocuments(companyId: string, documentIds: string[]): Promise<{ message: string; details: any }> {
    const response = await apiClient.post('/api/v1/admin/knowledge/documents/bulk-delete', {
      company_id: companyId,
      document_ids: documentIds
    })
    return response.data
  }

  async processDocument(documentId: string, processParams: DocumentProcessRequest): Promise<{ message: string; document_id: string; status: string; chunk_size: number; overlap_length: number; chunks_created: number }> {
    const response = await apiClient.post(`/api/v1/admin/knowledge/documents/${documentId}/process`, processParams)
    return response.data
  }

  async getDocumentProcessingStatus(documentId: string): Promise<DocumentProcessingStatus> {
    const response = await apiClient.get(`/api/v1/admin/knowledge/documents/${documentId}/status`)
    return response.data
  }

  // Knowledge Chunks
  async getKnowledgeChunks(companyId: string, limit: number = 100, offset: number = 0): Promise<{chunks: DocumentChunk[]}> {
    const response = await apiClient.get(`/api/v1/admin/knowledge/chunks?company_id=${companyId}&limit=${limit}&offset=${offset}`)
    return response.data
  }

  // Feedback Management
  async getFeedback(companyId: string, feedbackType?: string, limit: number = 100, offset: number = 0): Promise<FeedbackResponse[]> {
    let url = `/api/v1/admin/feedback?company_id=${companyId}&limit=${limit}&offset=${offset}`
    if (feedbackType) {
      url += `&feedback_type=${feedbackType}`
    }
    const response = await apiClient.get(url)
    return response.data
  }

  async getFeedbackStats(companyId: string): Promise<FeedbackStats> {
    const response = await apiClient.get(`/api/v1/admin/feedback/stats?company_id=${companyId}`)
    return response.data
  }

  async searchFeedback(companyId: string, searchTerm: string, limit: number = 100, offset: number = 0): Promise<FeedbackResponse[]> {
    const response = await apiClient.get(`/api/v1/admin/feedback/search?company_id=${companyId}&search_term=${searchTerm}&limit=${limit}&offset=${offset}`)
    return response.data
  }

  // Dashboard Metrics
  async getDashboardMetrics(): Promise<DashboardMetrics> {
    const response = await apiClient.get('/api/v1/admin/dashboard/metrics')
    return response.data
  }

  async getSystemSummary(): Promise<SystemSummary> {
    const response = await apiClient.get('/api/v1/admin/dashboard/summary')
    return response.data
  }
}

export const adminApi = new AdminApi()
export default adminApi
export type { Company, KnowledgeDocument, DocumentChunk, FeedbackStats, FeedbackResponse, CompanyCreate, DocumentProcessRequest, DocumentProcessingStatus, CompanyMetrics, DashboardMetrics, SystemSummary }