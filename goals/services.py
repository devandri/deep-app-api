from .schemas import GoalRequest
from .models import Goal, GoalChecklist
from typing import List, Optional
from django.shortcuts import get_object_or_404
from .repositories import GoalChecklistRepository
import logging
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

class GoalService:
    
    @staticmethod
    def create_goal(data: GoalRequest) -> Goal:
        return Goal.objects.create(
            name=data.name,
            category=data.category,
            objective=data.objective,
            start_date=data.start_date,
            end_date=data.end_date,
            description=data.description,
            status=data.status,
        )
        
    @staticmethod
    def get_goals() -> List[Goal]:
        # return {
        #     'success': True,
        #     'message': 'OK'
        # }
    # def get_goals():
        goals = Goal.objects.all()
        logger.info(goals)
        return goals
    
    @staticmethod
    def get_goal(goal_id: int) -> Optional[Goal]:
        # return Goal.objects.filter(id=goal_id, deleted_at__isnull=True)
        return get_object_or_404(Goal, id=goal_id)
    
    def create_checklist(**data) -> GoalChecklist:
        return GoalChecklistRepository.create(**data)
    
    def get_checklist(checklist_id: int) -> GoalChecklist:
        goal_checklist = GoalChecklistRepository.get_by_id(checklist_id)
        if goal_checklist is None:
            raise ValidationError("Goal checklist not found.")
        return goal_checklist
    
    def list_checklists() -> List[GoalChecklist]:
        return GoalChecklistRepository.all()