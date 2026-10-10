from ninja import Router, Query, Schema
from .services import GoalService
from .schemas import GoalSerializer, GoalRequest, GoalResource, GoalChecklistRequest, GoalChecklistResource
from utils.responses import ErrorResponse
from utils.auth import AuthBearer
from drf_spectacular.utils import extend_schema
from django.core.exceptions import ValidationError
from typing import List, Optional
from core.schemas import ApiResponse, ErrorResponse, ListData
from core.responses import ok
from core.exceptions import ApiError
from utils.responses import paginated
from pydantic import Field
import logging

logger = logging.getLogger(__name__)

goals_router = Router(tags=["Goals"])
checklists_router = Router(tags=["Checklists"])

class GoalListQuery(Schema):
    # filters
    search: Optional[str] = None
    name: Optional[str] = None
    
    # sorting
    sort_by: str = "created_at"
    sort_order: str = Field("desc", pattern="^(asc|desc)$")
    
    # pagination
    page: int = Field(1, ge=1)
    per_page: int = Field(10, ge=1, le=100)
    
    # soft-deleting scope
    include_deleted: bool = False
    only_deleted: bool = False

"""Goal"""
# create a new goal

# @goals_router.get(
#     "/",
#     response={},
#     auth=AuthBearer,
#     summary="List all goals"
# )

# def list_goals(
#     request
# ):
#     return 500, {
#         "success": True
#     }

@goals_router.post(
    "/",
    response={
        201: GoalResource,
        400: ErrorResponse
    },
    auth=AuthBearer(),
    summary="Create a new goal"
)
def create(request, payload: GoalRequest):
    try:
        goal = GoalService.create_goal(payload)
    except ValidationError as e:
        return 400, {"code": "validation_error", "message": str(e)}
    return 201, goal
      
# get goal lists  
@goals_router.get(
    "/",
    auth=AuthBearer(),
    response={
        # 200: List[GoalResource],
        # 200: ApiResponse[List[GoalResource]],
        200: ApiResponse[ListData[GoalResource]],
        500: ErrorResponse
    },
    summary="Get goal lists"
)
# @extend_schema(
#     responses={
#         200: GoalSerializer
#     }
# )
def list_goals(
    request, 
    params: GoalListQuery = Query(...)
):
    # result = GoalService.get_goals()
    # # return 200, result
    # return 200, ok(result, "Retreive goal successfully.")
    
    # return 200, result
    filters = {
        "search": params.search,
        "name": params.name
    }
    result = GoalService.list_checklist_extra(
        filters=filters,
        sort_by=params.sort_by,
        sort_order=params.sort_order,
        page=params.page,
        per_page=params.per_page
    )
    # return 200, ok(result["items"], "Retreive goal successfully.")
    # return 200, ok(result, "Retreive goal successfully.")
    return paginated(
        items=result["items"],
        pagination=result["pagination"],
        message="Users retrieved successfully",
    )


# get detail goal by id
@goals_router.get(
    "/{goal_id}",
    response={
        # 200: List[GoalResource]
        # 200: GoalResource
        200: ApiResponse[GoalResource]
    },
    auth=AuthBearer(),
    summary="Retreive detail goal"
)
def get_goal(request, goal_id: int):
    goal = GoalService.get_goal(goal_id)
    # return 200, goal
    return ok(goal)

# update goal

# delete goal

"""Checklist"""
# create a new checklist
@checklists_router.post(
    "/",
    response={
        201: GoalChecklistResource,
        400: ErrorResponse
    },
    auth=AuthBearer(),
    summary="Create a new checklist"
)
def create_checklist(request, payload: GoalChecklistRequest):
    try:
        checklist = GoalService.create_checklist(**payload.dict())
    except ValidationError as e:
        return 400, {"code": "validation_error", "message": str(e)}
    return 201, checklist

# get checklist lists
@checklists_router.get(
    "/",
    response={
        200: List[GoalChecklistResource]
    },
    auth=AuthBearer(),
    summary="Get all checklists"
)
def list_checklists(request):
    result = GoalService.list_checklists()
    return 200, result

# get detail checklist by id
@checklists_router.get(
    "/{checklist_id}",
    response={
        200: GoalChecklistResource,
        404: ErrorResponse
    },
    auth=AuthBearer(),
    summary="Get detail checklist"
)
def get_checklist(request, checklist_id: int):
    try:
        checklist = GoalService.get_checklist(checklist_id)
    except ValidationError as e:
        return 404, {"code": "not_found", "message": str(e)}
    return 200, checklist

# update checklist

# delete checklist