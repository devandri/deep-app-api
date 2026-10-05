from .schemas import GoalCreateSchema
from .models import Goal
from typing import List

class GoalService:
    
    @staticmethod
    def create_user(data: GoalCreateSchema) -> Goal:
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
        return {
            'success': True,
            'message': 'OK'
        }