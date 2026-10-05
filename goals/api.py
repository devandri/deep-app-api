from ninja import Router
from .services import GoalService
from .schemas import GoalCreateSchema
from utils.auth import AuthBearer

goals_router = Router(tags=["Goals"])

"""Goal"""
# create a new goal

# get goal lists
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

@goals_router.get(
    "/",
    # auth=AuthBearer()
)
def list_goals(
    request,
):
    result = GoalService.get_goals()
    return result


# get detail goal by id

# update goal

# delete goal

"""Checklist"""
# create a new checklist

# get checklist lists

# get detail checklist by id

# update checklist

# delete checklist