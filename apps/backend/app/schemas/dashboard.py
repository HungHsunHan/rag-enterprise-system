from typing import List
from pydantic import BaseModel


class CompanyMetrics(BaseModel):
    """Schema for company-specific metrics"""
    company_id: str
    company_name: str
    user_count: int
    document_count: int
    queries_today: int


class DashboardMetrics(BaseModel):
    """Schema for dashboard overview metrics"""
    total_companies: int
    shared_documents_count: int
    company_metrics: List[CompanyMetrics]
    timestamp: str


class SystemSummary(BaseModel):
    """Schema for system-wide summary metrics"""
    total_users: int
    total_documents: int
    total_queries_today: int
    total_companies: int