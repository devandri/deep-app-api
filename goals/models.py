from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import SoftDeleteModel

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
class Goal(SoftDeleteModel):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50)
    objective = models.CharField(max_length=200)
    start_date = models.DateField(blank=True, null=True, default=None)
    end_date = models.DateField(blank=True, null=True, default=None)
    description = models.TextField(blank=True, default="")
    status = models.CharField(max_length=20, null=True, blank=True, default="draft") # draft/progress/done
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
class GoalChecklist(SoftDeleteModel):
    goal = models.ForeignKey(
        Goal, on_delete=models.CASCADE, related_name='goal_checklists'
    )
    title = models.CharField(max_length=200)
    period = models.CharField(max_length=20)
    interval = models.PositiveIntegerField(null=True, blank=True, default=None) # every_n_days: 1,2,3, etc.
    day_of_week = models.CharField(
        max_length=9,
        choices=[
            ("monday", "Monday"),
            ("tuesday", "Tuesday"),
            ("wednesday", "Wednesday"),
            ("thursday", "Thursday"),
            ("friday", "Friday"),
            ("saturday", "Saturday"),
            ("sunday", "Sunday"),
        ],
        null=True, blank=True, default=None
    ) # weekly
    day_of_month = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(31),
        ],
        null=True, blank=True, default=None
    ) # monthly
    scheduled_date = models.DateField(null=True, blank=True, default=None) # yearly period: yyyy-mm-ddd
    description = models.TextField(blank=True, default="")
    is_auto_complete = models.BooleanField(default=False)
    is_auto_incomplete = models.BooleanField(default=False)
    status = models.CharField(max_length=20, null=True, blank=True, default=None) # active/inactive
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
class ChecklistLog(SoftDeleteModel):
    goal_checklist = models.ForeignKey(
        GoalChecklist, on_delete=models.CASCADE, related_name='checklist_logs'
    )
    title = models.CharField(max_length=200)
    period = models.CharField(max_length=20)
    description = models.TextField(blank=True, default="")
    is_auto_complete = models.BooleanField(default=False)
    is_auto_incomplete = models.BooleanField(default=False)
    is_complete = models.BooleanField(null=True, blank=True, default=None)
    completed_at = models.DateTimeField(null=True, blank=True, default=None)
    is_incomplete = models.BooleanField(null=True, blank=True, default=None)
    incompleted_at = models.DateTimeField(null=True, blank=True, default=None)
    date = models.DateField(blank=True, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)
    
    class Meta:
        db_table = 'checklist_log'
        ordering = ["-created_at"]

    def __str__(self):
        return self.title