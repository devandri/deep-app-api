from ninja import Schema
from typing import Optional
from datetime import date
from rest_framework import serializers

class GoalCreateSerialize(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    category = serializers.CharField(max_length=50)
    objective = serializers.CharField(max_length=200)
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    description = serializers.CharField()
    status = serializers.CharField()
    

class GoalCreateSchema(Schema):
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
