"""
Workflow Monitoring and Quality Assessment

This module contains classes for monitoring workflow execution, assessing quality,
and providing analytics for campaign generation processes.
"""

import time


class WorkflowMonitor:
    """
    Workflow monitoring system to track execution time, iterations, and performance metrics.
    
    Features:
    - Timeout management and detection
    - Iteration logging and analysis
    - Performance summary generation
    - Alert system for high iteration counts
    """
    
    def __init__(self, max_duration=300):  # 5 minutes default
        self.start_time = time.time()
        self.max_duration = max_duration
        self.iteration_log = []
    
    def check_timeout(self):
        """Check if workflow has exceeded maximum duration"""
        elapsed = time.time() - self.start_time
        if elapsed > self.max_duration:
            print(f"⏰ Timeout reached ({elapsed:.1f}s). Completing workflow.")
            return True
        return False
    
    def log_iteration(self, state):
        """Log iteration data for performance analysis"""
        iteration_data = {
            "timestamp": time.time(),
            "revision_count": state.get("revision_count", 0),
            "artifacts_count": len(state.get("artifacts", {})),
            "feedback_count": len(state.get("feedback", []))
        }
        self.iteration_log.append(iteration_data)
        
        # Alert if too many iterations
        if len(self.iteration_log) > 5:
            print("🚨 High iteration count detected. Consider manual intervention.")
    
    def get_summary(self):
        """Generate workflow execution summary"""
        if not self.iteration_log:
            return {"total_iterations": 0, "avg_artifacts": 0, "duration": 0}
        
        return {
            "total_iterations": len(self.iteration_log),
            "avg_artifacts": sum(log["artifacts_count"] for log in self.iteration_log) / len(self.iteration_log),
            "duration": self.iteration_log[-1]["timestamp"] - self.iteration_log[0]["timestamp"] if self.iteration_log else 0
        }


class QualityChecker:
    """
    Quality assessment system for evaluating campaign content and workflow decisions.
    
    Features:
    - Content completeness scoring
    - Change detection between iterations
    - Feedback sentiment analysis
    - Quality threshold enforcement
    """
    
    @staticmethod
    def assess_quality(state):
        """
        Assess overall campaign quality based on artifact completeness
        
        Args:
            state: Current workflow state
            
        Returns:
            int: Quality score (0-100)
        """
        artifacts = state.get("artifacts", {})
        quality_score = 0
        
        # Score based on content completeness and length
        if artifacts.get("strategy"):
            quality_score += 20
        if artifacts.get("creative_concepts"):
            quality_score += 20
        if artifacts.get("copy"):
            quality_score += 20
        if artifacts.get("visual", {}).get("image_url"):
            quality_score += 20
        if artifacts.get("audience_personas"):
            quality_score += 10
        if artifacts.get("cta_optimization"):
            quality_score += 10
        
        return quality_score
    
    @staticmethod
    def has_significant_changes(state):
        """
        Detect significant changes between current and previous artifacts
        
        Args:
            state: Current workflow state
            
        Returns:
            bool: True if significant changes detected
        """
        current_artifacts = state.get("artifacts", {})
        previous_artifacts = state.get("previous_artifacts", {})
        
        # Compare current vs previous artifacts
        changes = 0
        for key in current_artifacts:
            if key not in previous_artifacts:
                changes += 1
            elif current_artifacts[key] != previous_artifacts[key]:
                changes += 1
        
        # Store current as previous for next iteration
        state["previous_artifacts"] = current_artifacts.copy()
        
        return changes >= 2  # Threshold for "significant" changes
    
    @staticmethod
    def analyze_feedback_quality(state):
        """
        Analyze feedback sentiment to determine workflow progression
        
        Args:
            state: Current workflow state
            
        Returns:
            str: 'complete' or 'continue_revision'
        """
        feedback = state.get("feedback", [])
        
        if not feedback:
            return "complete"
        
        last_feedback = str(feedback[-1]).lower()
        
        # Check for positive feedback indicators
        positive_indicators = ["good", "great", "excellent", "approved", "satisfied", "perfect"]
        negative_indicators = ["revise", "change", "improve", "fix", "wrong", "bad", "needs"]
        
        positive_count = sum(1 for indicator in positive_indicators if indicator in last_feedback)
        negative_count = sum(1 for indicator in negative_indicators if indicator in last_feedback)
        
        # Exit on positive feedback
        if positive_count > negative_count:
            print("✅ Positive feedback detected. Completing workflow.")
            return "complete"
        
        # Continue only on negative feedback
        if negative_count > 0:
            return "continue_revision"
        
        return "complete"


class CampaignAnalytics:
    """
    Campaign analytics system for tracking performance and generating insights.
    
    Features:
    - Iteration tracking and performance metrics
    - Team performance analysis
    - Quality scoring and trend analysis
    - Recommendation generation
    """
    
    def __init__(self):
        self.metrics = {
            "iterations": 0,
            "team_performance": {},
            "quality_scores": {},
            "timing": {}
        }
    
    def track_iteration(self, state: dict):
        """Track iteration metrics and team performance"""
        self.metrics["iterations"] += 1
        # Add performance tracking for each team
        for team, artifact in state.get('artifacts', {}).items():
            if team not in self.metrics["team_performance"]:
                self.metrics["team_performance"][team] = []
            
            # Calculate artifact length/complexity
            artifact_size = len(str(artifact)) if artifact else 0
            self.metrics["team_performance"][team].append(artifact_size)
    
    def generate_report(self) -> dict:
        """Generate comprehensive analytics report"""
        return {
            "summary": self._generate_summary(),
            "recommendations": self._generate_recommendations(),
            "performance": self.metrics
        }
    
    def _generate_summary(self):
        """Generate executive summary of campaign generation"""
        return f"Campaign generated in {self.metrics['iterations']} iterations"
    
    def _generate_recommendations(self):
        """Generate recommendations based on performance analysis"""
        recommendations = []
        
        # Analyze team performance
        for team, performances in self.metrics["team_performance"].items():
            if performances:
                avg_performance = sum(performances) / len(performances)
                if avg_performance < 100:  # Example threshold
                    recommendations.append(f"Consider providing more detailed input to {team}")
        
        return recommendations 