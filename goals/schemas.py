from ninja import Schema
from typing import Optional
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
    description: Optional[str]
    is_auto_complete: Optional[bool] = False
    is_auto_incomplete: Optional[bool] = False
    
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
    
class GoalChecklistResource(Schema):
    id: int
    title: str
    goal: Optional[GoalSchema] = None
    period: str
    description: Optional[str]
    is_auto_complete: Optional[bool] = False
    is_auto_incomplete: Optional[bool] = False
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