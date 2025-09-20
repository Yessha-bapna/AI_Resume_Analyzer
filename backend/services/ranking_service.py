from __init__ import db
from models import ResumeAnalysis
from datetime import datetime
from typing import List, Dict
import threading

class RankingService:
    def __init__(self):
        self._lock = threading.Lock()
    
    def add_to_queue(self, analysis_id: int, job_id: int) -> int:
        """Add a new analysis to the queue and return queue position"""
        with self._lock:
            try:
                # Get the last queue position for this job
                last_position = db.session.query(db.func.max(ResumeAnalysis.queue_position))\
                    .filter(ResumeAnalysis.job_id == job_id)\
                    .scalar() or 0
                
                # Set queue position (1-based)
                queue_position = last_position + 1
                
                # Update the analysis record
                analysis = ResumeAnalysis.query.get(analysis_id)
                if analysis:
                    analysis.queue_position = queue_position
                    analysis.is_in_queue = True
                    analysis.analysis_status = 'pending'
                    db.session.commit()
                
                return queue_position
            except Exception as e:
                db.session.rollback()
                raise Exception(f"Error adding to queue: {str(e)}")
    
    def add_to_ranking(self, analysis: ResumeAnalysis) -> None:
        """Add a completed analysis to the ranking system"""
        with self._lock:
            try:
                # Update ranking for this job
                self.update_ranking(analysis.job_id, analysis)
            except Exception as e:
                db.session.rollback()
                raise Exception(f"Error adding to ranking: {str(e)}")
    
    def update_ranking(self, job_id: int, new_analysis: ResumeAnalysis = None) -> List[ResumeAnalysis]:
        """Update rankings when a new analysis is completed or for re-ranking all analyses"""
        with self._lock:
            try:
                # Get all analyses for this job ordered by relevance score (descending)
                analyses = ResumeAnalysis.query\
                    .filter(ResumeAnalysis.job_id == job_id)\
                    .filter(ResumeAnalysis.analysis_status == 'completed')\
                    .order_by(ResumeAnalysis.relevance_score.desc())\
                    .all()
                
                # Update ranks (1-based ranking)
                for i, analysis in enumerate(analyses):
                    old_rank = analysis.rank
                    new_rank = i + 1
                    analysis.rank = new_rank
                    
                    # If rank changed significantly, log it
                    if old_rank is not None and abs(old_rank - new_rank) > 0:
                        print(f"Analysis {analysis.id} rank changed from {old_rank} to {new_rank}")
                    elif old_rank is None:
                        print(f"Analysis {analysis.id} assigned new rank: {new_rank}")
                
                db.session.commit()
                return analyses
            except Exception as e:
                db.session.rollback()
                raise Exception(f"Error updating ranking: {str(e)}")
    
    def promote_high_score_resume(self, job_id: int, min_score: float = 80.0) -> bool:
        """Promote high-scoring resumes to top of ranking"""
        with self._lock:
            try:
                # Find high-scoring analyses that aren't already top-ranked
                high_score_analyses = ResumeAnalysis.query\
                    .filter(ResumeAnalysis.job_id == job_id)\
                    .filter(ResumeAnalysis.relevance_score >= min_score)\
                    .filter(ResumeAnalysis.analysis_status == 'completed')\
                    .filter(ResumeAnalysis.rank > 1)\
                    .order_by(ResumeAnalysis.relevance_score.desc())\
                    .all()
                
                if not high_score_analyses:
                    return False
                
                # Get the best high-scoring analysis
                best_analysis = high_score_analyses[0]
                
                # Get current #1 analysis
                current_top = ResumeAnalysis.query\
                    .filter(ResumeAnalysis.job_id == job_id)\
                    .filter(ResumeAnalysis.rank == 1)\
                    .first()
                
                if current_top and best_analysis.relevance_score > current_top.relevance_score:
                    # Swap ranks
                    old_top_rank = current_top.rank
                    current_top.rank = best_analysis.rank
                    best_analysis.rank = old_top_rank
                    
                    db.session.commit()
                    
                    # Re-rank all other analyses
                    self._rerank_after_promotion(job_id)
                    
                    return True
                
                return False
            except Exception as e:
                db.session.rollback()
                raise Exception(f"Error promoting high-score resume: {str(e)}")
    
    def _rerank_after_promotion(self, job_id: int):
        """Re-rank all analyses after a promotion"""
        try:
            # Get all completed analyses for this job, ordered by relevance score
            analyses = ResumeAnalysis.query\
                .filter(ResumeAnalysis.job_id == job_id)\
                .filter(ResumeAnalysis.analysis_status == 'completed')\
                .order_by(ResumeAnalysis.relevance_score.desc())\
                .all()
            
            # Assign new ranks
            for i, analysis in enumerate(analyses):
                analysis.rank = i + 1
            
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error re-ranking: {str(e)}")
    
    def get_job_rankings(self, job_id: int, limit: int = None) -> List[Dict]:
        """Get current rankings for a job"""
        try:
            # First, ensure all analyses have proper ranks
            self.update_ranking(job_id, None)
            
            # Get analyses ordered by relevance score (descending) for proper ranking
            query = ResumeAnalysis.query\
                .filter(ResumeAnalysis.job_id == job_id)\
                .filter(ResumeAnalysis.analysis_status == 'completed')\
                .order_by(ResumeAnalysis.relevance_score.desc())
            
            if limit:
                query = query.limit(limit)
            
            analyses = query.all()
            
            # Add detailed ranking information
            detailed_rankings = []
            for i, analysis in enumerate(analyses):
                rank_data = analysis.to_dict()
                rank_data['rank'] = i + 1  # Ensure proper 1-based ranking
                rank_data['rank_explanation'] = self._get_rank_explanation(analysis, i + 1)
                rank_data['improvement_areas'] = self._get_improvement_areas(analysis)
                detailed_rankings.append(rank_data)
            
            return detailed_rankings
        except Exception as e:
            raise Exception(f"Error getting rankings: {str(e)}")
    
    def _get_rank_explanation(self, analysis: ResumeAnalysis, rank: int) -> str:
        """Generate explanation for why this candidate has this rank"""
        score = analysis.relevance_score
        verdict = analysis.verdict
        
        if rank == 1:
            if score >= 90:
                return f"Top candidate with exceptional score of {score:.1f}%. Demonstrates excellent fit for the role with {verdict.lower()} suitability."
            elif score >= 80:
                return f"Leading candidate with strong score of {score:.1f}%. Shows {verdict.lower()} suitability and good alignment with job requirements."
            else:
                return f"Currently ranked #1 with score of {score:.1f}%, though there's room for improvement to reach {verdict.lower()} suitability."
        else:
            if score >= 80:
                return f"Strong candidate ranked #{rank} with {score:.1f}% score. Shows {verdict.lower()} suitability but other candidates scored higher."
            elif score >= 70:
                return f"Moderate candidate ranked #{rank} with {score:.1f}% score. Shows {verdict.lower()} suitability with potential for improvement."
            else:
                return f"Candidate ranked #{rank} with {score:.1f}% score. Shows {verdict.lower()} suitability and significant room for improvement."
    
    def _get_improvement_areas(self, analysis: ResumeAnalysis) -> Dict:
        """Get detailed improvement suggestions"""
        missing_skills = analysis.get_missing_skills() or []
        missing_certifications = analysis.get_missing_certifications() or []
        missing_projects = analysis.get_missing_projects() or []
        improvement_suggestions = analysis.improvement_suggestions or ""
        
        return {
            'missing_skills': missing_skills,
            'missing_certifications': missing_certifications,
            'missing_projects': missing_projects,
            'general_suggestions': improvement_suggestions.split('\n') if improvement_suggestions else [],
            'priority_level': self._get_priority_level(analysis.relevance_score),
            'improvement_potential': self._get_improvement_potential(analysis.relevance_score)
        }
    
    def _get_priority_level(self, score: float) -> str:
        """Determine priority level for improvement"""
        if score >= 90:
            return "Low - Already excellent"
        elif score >= 80:
            return "Medium - Minor improvements needed"
        elif score >= 70:
            return "High - Significant improvements needed"
        else:
            return "Critical - Major improvements required"
    
    def _get_improvement_potential(self, score: float) -> str:
        """Estimate improvement potential"""
        if score >= 90:
            return "Limited - Already near perfect"
        elif score >= 80:
            return "Moderate - Can reach 90%+ with targeted improvements"
        elif score >= 70:
            return "High - Can reach 80%+ with focused development"
        else:
            return "Very High - Can significantly improve with comprehensive skill development"
    
    def get_queue_status(self, job_id: int) -> Dict:
        """Get queue status for a job"""
        try:
            total_in_queue = ResumeAnalysis.query\
                .filter(ResumeAnalysis.job_id == job_id)\
                .filter(ResumeAnalysis.is_in_queue == True)\
                .count()
            
            pending_analyses = ResumeAnalysis.query\
                .filter(ResumeAnalysis.job_id == job_id)\
                .filter(ResumeAnalysis.analysis_status == 'pending')\
                .count()
            
            processing_analyses = ResumeAnalysis.query\
                .filter(ResumeAnalysis.job_id == job_id)\
                .filter(ResumeAnalysis.analysis_status == 'processing')\
                .count()
            
            completed_analyses = ResumeAnalysis.query\
                .filter(ResumeAnalysis.job_id == job_id)\
                .filter(ResumeAnalysis.analysis_status == 'completed')\
                .count()
            
            return {
                'total_in_queue': total_in_queue,
                'pending': pending_analyses,
                'processing': processing_analyses,
                'completed': completed_analyses,
                'estimated_wait_time': pending_analyses * 2  # Rough estimate in minutes
            }
        except Exception as e:
            raise Exception(f"Error getting queue status: {str(e)}")
    
    def remove_from_queue(self, analysis_id: int):
        """Remove an analysis from the queue"""
        with self._lock:
            try:
                analysis = ResumeAnalysis.query.get(analysis_id)
                if analysis:
                    analysis.is_in_queue = False
                    analysis.queue_position = 0
                    db.session.commit()
            except Exception as e:
                db.session.rollback()
                raise Exception(f"Error removing from queue: {str(e)}")
    
    def get_next_in_queue(self, job_id: int) -> ResumeAnalysis:
        """Get the next analysis to process from the queue"""
        try:
            next_analysis = ResumeAnalysis.query\
                .filter(ResumeAnalysis.job_id == job_id)\
                .filter(ResumeAnalysis.is_in_queue == True)\
                .filter(ResumeAnalysis.analysis_status == 'pending')\
                .order_by(ResumeAnalysis.queue_position.asc())\
                .first()
            
            if next_analysis:
                # Mark as processing
                next_analysis.analysis_status = 'processing'
                next_analysis.analysis_started_at = datetime.utcnow()
                db.session.commit()
            
            return next_analysis
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error getting next in queue: {str(e)}")

# Global ranking service instance
ranking_service = RankingService()
