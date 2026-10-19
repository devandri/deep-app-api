from ninja import Router, Query, Schema
from .services import GoalService
from .schemas import GoalSerializer, GoalRequest, GoalResource, GoalChecklistRequest, GoalChecklistRequestV2, GoalChecklistResource, BulkDeleteRequest, BulkDeleteResponse
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
from django.db.models import QuerySet
from django.db import transaction
from .models import Goal
import logging

logger = logging.getLogger(__name__)

goals_router = Router(tags=["Goals"])
checklists_router = Router(tags=["Checklists"])

class GoalListQuery(Schema):
    # filters
    search: Optional[str] = None
    name: Optional[str] = None
    status: Optional[str] = None
    
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
        "name": params.name,
        "status": params.status,
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
@goals_router.put(
    "/{goal_id}",
    response={
        200: ApiResponse[GoalResource],
        404: ErrorResponse,
        422: ErrorResponse,
    },
    auth=AuthBearer(),
    summary="Update goal",
    description=""
)
def update_goal(request, goal_id: int, payload: GoalRequest):
    try:
        exist_goal = Goal.objects.get(id=goal_id)
        if not exist_goal:
            return 404, { "code": "not_found", "message": "Goal not found."}
        
        goal = GoalService.update_goal(goal_id, exist_goal, payload)
        return ok(goal)
    except Exception as e:
        return 422, { "code": "exception", "message": str(e) }
    
@goals_router.get(
    "/{goal_id}/checklist",
    response={
        200: List[GoalChecklistResource]
    },
    auth=AuthBearer(),
    summary="Get all checklists"
)
def list_goal_checklists(request, goal_id: int):
    result = GoalService.list_checklists_by_goal_id(goal_id)
    return 200, result

@goals_router.post(
    "/{goal_id}/checklist",
    response={
        201: GoalChecklistResource,
        400: ErrorResponse
    },
    auth=AuthBearer(),
    summary="Create a new checklist"
)
def create_goal_checklist(request, goal_id: int, payload: GoalChecklistRequestV2):
    data = payload.dict()
    data["goal_id"] = goal_id
    # payload.goal_id = goal_id
    try:
        checklist = GoalService.create_checklist(**data)
    except ValidationError as e:
        return 400, {"code": "validation_error", "message": str(e)}
    except Exception as e:
        return 400, {"code": "validation_error", "message": str(e)}
    return 201, checklist

@goals_router.put(
    "/{goal_id}/checklist/{checklist_id}",
    response={
        201: GoalChecklistResource,
        400: ErrorResponse
    },
    auth=AuthBearer(),
    summary="Create a new checklist"
)
def update_goal_checklist(request, goal_id: int, checklist_id: int, payload: GoalChecklistRequestV2):
    try:
        checklist = GoalService.update_goal_checklist(checklist_id, goal_id, payload)
    except ValidationError as e:
        return 400, {"code": "validation_error", "message": str(e)}
    except Exception as e:
        return 400, {"code": "exception_error", "message": str(e)}
    return 201, checklist

@goals_router.delete(
    "/{goal_id}/checklist/{checklist_id}",
    response={
        204: None,
        404: ErrorResponse
    },
    auth=AuthBearer(),
    summary="Soft delete goal",
    description=""
)
def delete_goal_checklist(request, goal_id: int, checklist_id: int):
    try:
        goal = GoalService.get_goal(goal_id)
    except ValidationError as e:
        return 404, { "code": "not_found", "messsage": str(e) }
    
    GoalService.delete_goal(goal)
    return 204, None

# delete goal
@goals_router.delete(
    "/{goal_id}",
    response={
        204: None,
        404: ErrorResponse
    },
    auth=AuthBearer(),
    summary="Soft delete goal",
    description=""
)
def delete_goal(request, goal_id: int):
    try:
        goal = GoalService.get_goal(goal_id)
    except ValidationError as e:
        return 404, { "code": "not_found", "messsage": str(e) }
    
    GoalService.delete_goal(goal)
    return 204, None

# bulk delete goal
@goals_router.delete(
    "/bulk/",
    response=BulkDeleteResponse,
    auth=AuthBearer(),
    summary="Bulk soft delete goal",
    description="",
)
def bulk_delete_goals(request, payload: BulkDeleteRequest):
    queryset: QuerySet[Goal] = Goal.objects.filter(
        # Example: category=request.goal.category
    )
    # requested_ids = List(dict.fromkeys(payload.ids))
    requested_ids = list(dict.fromkeys(payload.ids))
    
    with transaction.atomic():
        existing_ids = set(
            queryset.filter(id__in=requested_ids).values_list("id", flat=True)
        )
        
        deleted_ids = existing_ids
        
        if deleted_ids:
            queryset.filter(id__in=deleted_ids).delete()
            
        return {
            "requested": len(requested_ids),
            "deleted": len(deleted_ids),
            "not_found": [
                goal_id
                for goal_id in requested_ids
                if goal_id not in existing_ids
                
            ]
        }

"""Checklist"""
# create a new checklist
@checklists_router.post(
    "/",
    response={
        201: GoalChecklistResource,
        400: ErrorResponse,
        404: ErrorResponse,
        500: ErrorResponse,
    },
    auth=AuthBearer(),
    summary="Create a new checklist"
)
def create_checklist(request, payload: GoalChecklistRequest):
    try:
        checklist = GoalService.create_checklist(**payload.dict())
    except ValidationError as e:
        return 400, {"code": "validation_error", "message": str(e)}
    except Exception as e:
        return 500, {"code": "exception", "message": str(e)}
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
        404: ErrorResponse,
        500: ErrorResponse,
    },
    auth=AuthBearer(),
    summary="Get detail checklist"
)
def get_checklist(request, checklist_id: int):
    try:
        checklist = GoalService.get_checklist(checklist_id)
    except ValidationError as e:
        return 404, {"code": "not_found", "message": str(e)}
    except Exception as e:
        return 500, {"code": "exception", "message": str(e)}
    return 200, checklist

# update checklist

# delete checklist