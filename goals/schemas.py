from ninja import Schema
from typing import Optional, List
from datetime import date, datetime
from rest_framework import serializers
from pydantic import Field

class GoalSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    category = serializers.CharField(max_length=50)
    objective = serializers.CharField(max_length=200)
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    description = serializers.CharField()
    status = serializers.CharField()
    
class GoalChecklistSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    goal = GoalSerializer()
    title = serializers.CharField(max_length=200)
    period = serializers.CharField(max_length=20)
    description = serializers.CharField()
    is_auto_complete = serializers.BooleanField()
    is_auto_incomplete = serializers.BooleanField()


class GoalSchema(Schema):
    name: str
    category: str
    objective: str
    start_date: Optional[date]
    end_date: Optional[date]
    description: Optional[str]
    status: str
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

class GoalChecklistSchema(Schema):
    id: int
    title: str
    goal: Optional[GoalSchema] = None
    period: str
    status: str | None = None
    description: Optional[str]
    is_auto_complete: Optional[bool] = False
    is_auto_incomplete: Optional[bool] = False
    
class ChecklistLogResourceWithGoal(Schema):
    id: int
    title: str
    period: str
    description: Optional[str]
    is_auto_complete: Optional[bool] = False
    is_complete: Optional[bool] | None = None
    completed_at: datetime | None = None
    is_auto_incomplete: Optional[bool] = False
    is_incomplete: Optional[bool] | None = None
    incompleted_at: datetime | None = None
    date: date
    created_at: datetime
    updated_at: datetime
    
class GoalResourceWithChecklists(Schema):
    id: int
    title: str
    period: str
    description: Optional[str]
    is_auto_complete: Optional[bool] = False
    is_auto_incomplete: Optional[bool] = False
    status: str | None = None
    created_at: datetime
    updated_at: datetime
    checklist_log: Optional[ChecklistLogResourceWithGoal] = None
    
class GoalResource(Schema):
    id: int
    name: str
    category: str
    objective: str
    start_date: Optional[date]
    end_date: Optional[date]
    description: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
    goal_checklists: List[GoalResourceWithChecklists]
    
class GoalChecklistResource(Schema):
    id: int
    title: str
    goal: Optional[GoalSchema] = None
    period: str
    description: Optional[str]
    is_auto_complete: Optional[bool] = False
    is_auto_incomplete: Optional[bool] = False
    status: str | None = None
    created_at: datetime
    updated_at: datetime
    
class ChecklistLogResource(Schema):
    id: int
    title: str
    goal_checklist: Optional[GoalChecklistSchema] = None
    period: str
    description: Optional[str]
    is_auto_complete: Optional[bool] = False
    is_complete: Optional[bool] | None = None
    completed_at: datetime | None = None
    is_auto_incomplete: Optional[bool] = False
    is_incomplete: Optional[bool] | None = None
    incompleted_at: datetime | None = None
    date: date
    created_at: datetime
    updated_at: datetime
    
class GoalRequest(Schema):
    name: str
    category: str
    objective: str
    start_date: Optional[date]
    end_date: Optional[date]
    description: Optional[str]
    status: str
    
class GoalChecklistRequest(Schema):
    title: str
    goal_id: int
    period: str
    description: Optional[str]
    is_auto_complete: Optional[bool] = False
    is_auto_incomplete: Optional[bool] = False
    
class GoalChecklistRequestV2(Schema):
    title: str = Field(...)
    period: str
    description: Optional[str]
    is_auto_complete: Optional[bool] = False
    is_auto_incomplete: Optional[bool] = False
    
class GoalFilterParams(Schema):
    name: Optional[str] = Field(None, description="Filter by name (contains)")
    search: Optional[str] = Field(None, description="Search by all available columns")
    
class SortParams(Schema):
    sort_by: Optional[str] = Field(
        'created_at',
        description="Sort field: name, category..."
    )
    sort_order: Optional[str] = Field(
        'desc',
        description="",
        pattern="^(asc|desc)$"
    )
    
class BulkDeleteRequest(Schema):
    # ids: List[int] = Field(min_length=1, max_length=100)
    ids: list[int] = Field(min_length=1, max_length=100)
    
class BulkDeleteResponse(Schema):
    requested: int
    deleted: int
    not_found: List[int]
    
class ToggleGoalChecklistRequest(Schema):
    date: date
    is_complete: bool
    is_incomplete: bool