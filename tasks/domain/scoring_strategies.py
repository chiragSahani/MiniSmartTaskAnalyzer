from abc import ABC, abstractmethod
from datetime import date

class BaseScoringStrategy(ABC):
    @abstractmethod
    def score_tasks(self, tasks, config=None, today=None):
        """
        tasks: iterable of domain task objects/dicts
        config: optional configuration overrides
        today: optional reference date (defaults to date.today())
        
        returns: list of enriched task dicts with score, priority_level, explanation
        """
        pass

    def _get_today(self, today=None):
        return today or date.today()

    def _determine_priority_level(self, score, thresholds):
        if score >= thresholds.get("HIGH", 8.0):
            return "High"
        elif score >= thresholds.get("MEDIUM", 5.0):
            return "Medium"
        return "Low"

class FastestWinsStrategy(BaseScoringStrategy):
    def score_tasks(self, tasks, config=None, today=None):
        # Prioritize low effort (estimated_hours)
        # Score = 10 - estimated_hours (clamped at 1)
        # Or simply inverse of hours.
        # Let's use a simple linear scale: 1 hour = 10 points, 10 hours = 1 point.
        
        scored_tasks = []
        for task in tasks:
            hours = task.get('estimated_hours', 0) or 0
            if hours <= 0: hours = 0.5 # Avoid division by zero or negative
            
            # Simple formula: 10 / hours, capped at 10
            raw_score = 10.0 / hours if hours > 0 else 10.0
            score = min(raw_score, 10.0)
            
            scored_tasks.append({
                **task,
                'score': round(score, 2),
                'priority_level': self._determine_priority_level(score, {}), # Use default thresholds
                'explanation': f"Fastest Win: {hours} hours estimated."
            })
        
        # Sort by score desc
        scored_tasks.sort(key=lambda x: x['score'], reverse=True)
        return scored_tasks

class HighImpactStrategy(BaseScoringStrategy):
    def score_tasks(self, tasks, config=None, today=None):
        # Prioritize importance directly
        scored_tasks = []
        for task in tasks:
            importance = task.get('importance', 0) or 0
            score = float(importance)
            
            scored_tasks.append({
                **task,
                'score': round(score, 2),
                'priority_level': self._determine_priority_level(score, {}),
                'explanation': f"High Impact: Importance {importance}/10."
            })
            
        scored_tasks.sort(key=lambda x: x['score'], reverse=True)
        return scored_tasks

class DeadlineDrivenStrategy(BaseScoringStrategy):
    def score_tasks(self, tasks, config=None, today=None):
        today = self._get_today(today)
        scored_tasks = []
        
        for task in tasks:
            due_date = task.get('due_date')
            if not due_date:
                score = 0.0
                explanation = "No due date."
            else:
                # Convert string to date if needed
                if isinstance(due_date, str):
                    try:
                        due_date = date.fromisoformat(due_date)
                    except ValueError:
                        due_date = None
                
                if due_date:
                    days_until = (due_date - today).days
                    if days_until < 0:
                        score = 10.0 # Overdue is max priority
                        explanation = f"Overdue by {abs(days_until)} days."
                    elif days_until == 0:
                        score = 9.0
                        explanation = "Due today."
                    else:
                        # Decay score as due date is further away
                        # 1 day = 8, 7 days = 2
                        score = max(0.0, 9.0 - days_until)
                        explanation = f"Due in {days_until} days."
                else:
                    score = 0.0
                    explanation = "Invalid due date."

            scored_tasks.append({
                **task,
                'score': round(score, 2),
                'priority_level': self._determine_priority_level(score, {}),
                'explanation': explanation
            })
            
        scored_tasks.sort(key=lambda x: x['score'], reverse=True)
        return scored_tasks

class SmartBalanceStrategy(BaseScoringStrategy):
    def score_tasks(self, tasks, config=None, today=None):
        today = self._get_today(today)
        weights = config.get('weights') if config else None
        if not weights:
            from .scoring_config import DEFAULT_SMART_BALANCE_WEIGHTS
            weights = DEFAULT_SMART_BALANCE_WEIGHTS
            
        scored_tasks = []
        for task in tasks:
            # 1. Urgency Score (0-10)
            urgency_score = 0.0
            due_date = task.get('due_date')
            if due_date:
                if isinstance(due_date, str):
                    try:
                        due_date = date.fromisoformat(due_date)
                    except ValueError:
                        due_date = None
                
                if due_date:
                    days_until = (due_date - today).days
                    if days_until < 0: urgency_score = 10.0
                    elif days_until == 0: urgency_score = 9.0
                    else: urgency_score = max(0.0, 9.0 - (days_until * 0.5)) # Slower decay
            
            # 2. Importance Score (0-10)
            importance = float(task.get('importance', 0) or 0)
            
            # 3. Effort Score (0-10, lower effort = higher score)
            hours = task.get('estimated_hours', 0) or 0
            if hours <= 0: hours = 5.0 # Default if missing
            effort_score = max(0.0, 10.0 - (hours * 0.5)) # 20 hours = 0 score
            
            # 4. Dependency Score (Simple: count of dependents - tasks waiting on this)
            # Note: This requires a pre-calculated 'dependent_count' or similar.
            # For now, we'll assume the task dict might have it, or we ignore it.
            # Let's assume 'dependents_count' is passed in.
            dependents_count = task.get('dependents_count', 0)
            dependency_score = min(10.0, dependents_count * 2.0)
            
            # Weighted Sum
            total_score = (
                (urgency_score * weights.get('urgency', 0)) +
                (importance * weights.get('importance', 0)) +
                (effort_score * weights.get('effort', 0)) +
                (dependency_score * weights.get('dependencies', 0))
            )
            
            # Normalize to 0-10 if weights sum is approx 1
            # (Assuming weights sum to 1.0)
            
            scored_tasks.append({
                **task,
                'score': round(total_score, 2),
                'priority_level': self._determine_priority_level(total_score, {}),
                'explanation': f"Smart Score: {total_score:.1f} (U:{urgency_score:.1f}, I:{importance}, E:{effort_score:.1f})"
            })
            
        scored_tasks.sort(key=lambda x: x['score'], reverse=True)
        return scored_tasks

