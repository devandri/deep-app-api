from .models import Goal, GoalChecklist

class GoalChecklistRepository:
    @staticmethod
    def create(**data):
        return GoalChecklist.objects.create(**data)
    
    @staticmethod
    def all():
        # return GoalChecklist.objects.select_related("goal_checklist").filter(deleted_at__isnull=True)
        return GoalChecklist.objects.filter(deleted_at__isnull=True)
    
    @staticmethod
    def list_by_goal_id(goal_id):
        # return GoalChecklist.objects.select_related("goal_checklist").filter(deleted_at__isnull=True)
        return GoalChecklist.objects.filter(goal_id=goal_id,deleted_at__isnull=True)
        
    @staticmethod
    def check_list_by_id_and_goal_id(id, goal_id):
        return GoalChecklist.objects.filter(id=id, goal_id=goal_id, deleted_at__isnull=True).first()
    
    @staticmethod
    def get_by_id(checklist_id = int):
        return GoalChecklist.objects.filter(id=checklist_id, deleted_at__isnull=True).first()
    
    @staticmethod
    def get_goal_by_id(goal_id = int):
        return Goal.objects.filter(id=goal_id, deleted_at__isnull=True).first()
    
    @staticmethod
    def delete(goal: Goal):
        goal.delete()
        
    @staticmethod
    def delete_goal_checklist(goal_checklist: GoalChecklist):
        goal_checklist.delete()