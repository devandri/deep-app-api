from .models import GoalChecklist

class GoalChecklistRepository:
    @staticmethod
    def create(**data):
        return GoalChecklist.objects.create(**data)
    
    @staticmethod
    def all():
        # return GoalChecklist.objects.select_related("goal_checklist").filter(deleted_at__isnull=True)
        return GoalChecklist.objects.filter(deleted_at__isnull=True)
    
    @staticmethod
    def get_by_id(checklist_id = int):
        return GoalChecklist.objects.filter(id=checklist_id, deleted_at__isnull=True).first()