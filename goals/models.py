from django.db import models

"""
id (PK)
name (string=200)
category (string=50)
objective (string=200)
start_date (date)
end_date (date)
description (text)
status (string=20)
"""
class Goal(models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50)
    objective = models.CharField(max_length=200)
    start_date = models.DateField(blank=True, null=True, default=None)
    end_date = models.DateField(blank=True, null=True, default=None)
    description = models.TextField(blank=True, default="")
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)
    
    class Meta:
        db_table = 'goal'
        verbose_name_plural = 'Goals'

    def __str__(self):
        return self.name

"""
id (PK)
goal_id (FK)
title (string=200)
period (string=20)
description (text)
is_auto_complete (boolean)
is_auto_incomplete (boolean)
"""
class GoalChecklist(models.Model):
    goal = models.ForeignKey(
        Goal, on_delete=models.CASCADE, related_name='goal_checklists'
    )
    title = models.CharField(max_length=200)
    period = models.CharField(max_length=20)
    description = models.TextField(blank=True, default="")
    is_auto_complete = models.BooleanField(default=False)
    is_auto_incomplete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)
    
    class Meta:
        db_table = 'goal_checklist'
        ordering = ["-created_at"]
        
    def __str__(self):
        return self.title

"""
id (PK)
goal_checklist_id (FK)
title (string=200)
period (string=20)
description (text)
is_complete (boolen)
is_incomplete (boolean)
completed_at (date_time)
"""
class ChecklistLog(models.Model):
    goal_checklist = models.ForeignKey(
        GoalChecklist, on_delete=models.CASCADE, related_name='checklist_logs'
    )
    title = models.CharField(max_length=200)
    period = models.CharField(max_length=20)
    description = models.TextField(blank=True, default="")
    is_auto_complete = models.BooleanField(default=False)
    is_auto_incomplete = models.BooleanField(default=False)
    is_complete = models.BooleanField(null=True, blank=True, default=None)
    is_incomplete = models.BooleanField(null=True, blank=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)
    
    class Meta:
        db_table = 'checklist_log'
        ordering = ["-created_at"]

    def __str__(self):
        return self.title