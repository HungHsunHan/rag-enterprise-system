from typing import Dict, List, Optional
from sqlalchemy.orm import Session
import logging
import re
from collections import Counter

from app.db.models import FeedbackLog, DocumentChunk
from app.services.feedback_service import get_feedback_list

logger = logging.getLogger(__name__)


class QualityAssessmentService:
    """
    Service for assessing answer quality based on various metrics
    """
    
    def __init__(self):
        self.min_answer_length = 20
        self.max_answer_length = 1000
        self.quality_keywords = [
            'according to', 'based on', 'policy states', 'guidelines indicate',
            'procedure requires', 'company policy', 'regulation', 'handbook'
        ]
    
    def assess_answer_quality(self, question: str, answer: str, context_chunks: List[DocumentChunk]) -> Dict:
        """
        Assess the quality of an answer based on multiple criteria
        
        Returns a dictionary with quality metrics and overall score
        """
        try:
            # Initialize quality metrics
            metrics = {
                'length_score': self._assess_length(answer),
                'relevance_score': self._assess_relevance(question, answer),
                'context_usage_score': self._assess_context_usage(answer, context_chunks),
                'policy_reference_score': self._assess_policy_references(answer),
                'overall_score': 0.0,
                'quality_level': 'Unknown',
                'recommendations': []
            }
            
            # Calculate overall score (weighted average)
            weights = {
                'length_score': 0.2,
                'relevance_score': 0.3,
                'context_usage_score': 0.3,
                'policy_reference_score': 0.2
            }
            
            overall_score = sum(metrics[key] * weights[key] for key in weights.keys())
            metrics['overall_score'] = round(overall_score, 2)
            
            # Determine quality level
            if overall_score >= 0.8:
                metrics['quality_level'] = 'High'
            elif overall_score >= 0.6:
                metrics['quality_level'] = 'Medium'
            else:
                metrics['quality_level'] = 'Low'
            
            # Add recommendations
            metrics['recommendations'] = self._generate_recommendations(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error assessing answer quality: {e}")
            return {
                'length_score': 0.0,
                'relevance_score': 0.0,
                'context_usage_score': 0.0,
                'policy_reference_score': 0.0,
                'overall_score': 0.0,
                'quality_level': 'Error',
                'recommendations': ['Quality assessment failed']
            }
    
    def _assess_length(self, answer: str) -> float:
        """
        Assess answer length - too short or too long affects quality
        """
        length = len(answer.strip())
        
        if length < self.min_answer_length:
            return 0.3  # Too short
        elif length > self.max_answer_length:
            return 0.7  # Too long
        else:
            # Optimal length range
            optimal_min = 50
            optimal_max = 500
            if optimal_min <= length <= optimal_max:
                return 1.0
            elif length < optimal_min:
                return 0.6 + (length - self.min_answer_length) / (optimal_min - self.min_answer_length) * 0.4
            else:
                return 1.0 - (length - optimal_max) / (self.max_answer_length - optimal_max) * 0.3
    
    def _assess_relevance(self, question: str, answer: str) -> float:
        """
        Assess relevance by checking if answer addresses key terms from question
        """
        # Extract key terms from question (simple keyword extraction)
        question_words = set(re.findall(r'\b\w{4,}\b', question.lower()))
        answer_words = set(re.findall(r'\b\w{4,}\b', answer.lower()))
        
        # Calculate overlap
        if not question_words:
            return 0.5  # Default if no meaningful words
        
        overlap = len(question_words.intersection(answer_words))
        relevance_score = min(overlap / len(question_words), 1.0)
        
        return relevance_score
    
    def _assess_context_usage(self, answer: str, context_chunks: List[DocumentChunk]) -> float:
        """
        Assess how well the answer uses information from context chunks
        """
        if not context_chunks:
            return 0.0
        
        # Check if answer contains information from context
        answer_lower = answer.lower()
        context_usage = 0.0
        
        for chunk in context_chunks:
            chunk_words = set(re.findall(r'\b\w{5,}\b', chunk.chunk_text.lower()))
            answer_words = set(re.findall(r'\b\w{5,}\b', answer_lower))
            
            if chunk_words:
                overlap = len(chunk_words.intersection(answer_words))
                usage_ratio = overlap / len(chunk_words)
                context_usage = max(context_usage, usage_ratio)
        
        return min(context_usage * 2, 1.0)  # Amplify score but cap at 1.0
    
    def _assess_policy_references(self, answer: str) -> float:
        """
        Assess if answer references policies, procedures, or official sources
        """
        answer_lower = answer.lower()
        reference_count = 0
        
        for keyword in self.quality_keywords:
            if keyword in answer_lower:
                reference_count += 1
        
        # Score based on number of policy references found
        if reference_count >= 3:
            return 1.0
        elif reference_count >= 2:
            return 0.8
        elif reference_count >= 1:
            return 0.6
        else:
            return 0.3
    
    def _generate_recommendations(self, metrics: Dict) -> List[str]:
        """
        Generate recommendations based on quality metrics
        """
        recommendations = []
        
        if metrics['length_score'] < 0.5:
            recommendations.append("Consider providing more detailed answers")
        elif metrics['length_score'] < 0.8 and metrics['length_score'] > 0.9:
            recommendations.append("Answer might be too verbose - consider being more concise")
        
        if metrics['relevance_score'] < 0.6:
            recommendations.append("Ensure answer directly addresses the question asked")
        
        if metrics['context_usage_score'] < 0.5:
            recommendations.append("Better utilize information from company documents")
        
        if metrics['policy_reference_score'] < 0.6:
            recommendations.append("Include more references to company policies and procedures")
        
        if not recommendations:
            recommendations.append("Answer quality is good - maintain current standards")
        
        return recommendations
    
    def get_company_quality_overview(self, db: Session, company_id: str) -> Dict:
        """
        Get overall quality overview for a company based on feedback
        """
        try:
            # Get recent feedback
            feedback_list = get_feedback_list(db, company_id, limit=100)
            
            if not feedback_list:
                return {
                    'total_responses': 0,
                    'average_quality_score': 0.0,
                    'quality_distribution': {'High': 0, 'Medium': 0, 'Low': 0},
                    'satisfaction_rate': 0.0,
                    'common_issues': []
                }
            
            # Calculate satisfaction rate
            positive_count = sum(1 for f in feedback_list if f.feedback == 'POSITIVE')
            satisfaction_rate = (positive_count / len(feedback_list)) * 100
            
            # Mock quality scores for demonstration (in real implementation,
            # you would store quality assessments and retrieve them)
            quality_scores = []
            for feedback in feedback_list:
                # Simple heuristic: positive feedback = higher quality score
                if feedback.feedback == 'POSITIVE':
                    score = 0.8 + (len(feedback.answer) / 500) * 0.2
                else:
                    score = 0.4 + (len(feedback.answer) / 500) * 0.3
                quality_scores.append(min(score, 1.0))
            
            average_quality = sum(quality_scores) / len(quality_scores)
            
            # Quality distribution
            high_quality = sum(1 for score in quality_scores if score >= 0.8)
            medium_quality = sum(1 for score in quality_scores if 0.6 <= score < 0.8)
            low_quality = sum(1 for score in quality_scores if score < 0.6)
            
            # Common issues analysis
            negative_feedback = [f for f in feedback_list if f.feedback == 'NEGATIVE']
            common_issues = self._analyze_common_issues(negative_feedback)
            
            return {
                'total_responses': len(feedback_list),
                'average_quality_score': round(average_quality, 2),
                'quality_distribution': {
                    'High': high_quality,
                    'Medium': medium_quality,
                    'Low': low_quality
                },
                'satisfaction_rate': round(satisfaction_rate, 1),
                'common_issues': common_issues
            }
            
        except Exception as e:
            logger.error(f"Error getting quality overview: {e}")
            return {
                'total_responses': 0,
                'average_quality_score': 0.0,
                'quality_distribution': {'High': 0, 'Medium': 0, 'Low': 0},
                'satisfaction_rate': 0.0,
                'common_issues': []
            }
    
    def _analyze_common_issues(self, negative_feedback: List[FeedbackLog]) -> List[str]:
        """
        Analyze negative feedback to identify common issues
        """
        if not negative_feedback:
            return []
        
        # Simple keyword-based issue detection
        issue_keywords = {
            'Incomplete information': ['incomplete', 'not enough', 'need more', 'missing'],
            'Irrelevant response': ['not relevant', 'wrong answer', 'not related', 'off topic'],
            'Too generic': ['generic', 'vague', 'general', 'not specific'],
            'Outdated information': ['outdated', 'old', 'changed', 'updated']
        }
        
        detected_issues = []
        
        for issue_type, keywords in issue_keywords.items():
            count = 0
            for feedback in negative_feedback:
                answer_lower = feedback.answer.lower()
                question_lower = feedback.question.lower()
                
                for keyword in keywords:
                    if keyword in answer_lower or keyword in question_lower:
                        count += 1
                        break
            
            if count >= len(negative_feedback) * 0.2:  # At least 20% of negative feedback
                detected_issues.append(issue_type)
        
        return detected_issues[:3]  # Return top 3 issues


# Global instance
quality_service = QualityAssessmentService()