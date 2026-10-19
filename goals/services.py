from .schemas import GoalRequest
from .models import Goal, GoalChecklist
from typing import List, Optional, Any, Dict
from django.shortcuts import get_object_or_404
from .repositories import GoalChecklistRepository
import logging
from django.core.exceptions import ValidationError
from utils.services import ListService
from .filters import GOAL_FILTER_SPECS, GOAL_SORT_FIELDS

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
    def update_goal(goal_id, goal, data: GoalRequest) -> Goal:
        # goal = Goal.objects.get(id=goal_id)
        goal.name = data.name
        goal.category = data.category
        goal.objective = data.objective
        goal.start_date = data.start_date
        goal.end_date = data.end_date
        goal.description = data.description
        goal.status = data.status
        goal.save()
        return goal
        
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
    
    def list_checklists_by_goal_id(goal_id: int):
        return GoalChecklistRepository.list_by_goal_id(goal_id)
    
    def list_checklist_extra(
        filters: Dict[str, Any],
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        per_page: int = 10,
        included_deleted: bool = False,
        only_deleted: bool = False
    ) -> Dict[str, Any]:
        return ListService.get_list(
            model=Goal,
            filter_specs=GOAL_FILTER_SPECS,
            sort_fields=GOAL_SORT_FIELDS,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            per_page=per_page,
            include_deleted=included_deleted,
            only_deleted=only_deleted,
            default_sort="created_at"
        )
        
    def delete_goal(goal: Goal):
        GoalChecklistRepository.delete(goal)
        