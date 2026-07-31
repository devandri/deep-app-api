from ninja import Router

from .schemas import (
    UserCreateSchema,
    UserUpdateSchema,
    UserResponseSchema,
)

from .services import *

router = Router(tags=["Users"])


@router.get("/", response=list[UserResponseSchema])
def list_users(request):

    return get_users()


@router.get("/{user_id}", response=UserResponseSchema)
def detail(request, user_id: int):

    return get_user(user_id)


@router.post("/", response=UserResponseSchema)
def create(request, payload: UserCreateSchema):

    return create_user(payload)


@router.put("/{user_id}", response=UserResponseSchema)
def update(request, user_id: int, payload: UserUpdateSchema):

    return update_user(user_id, payload)


@router.delete("/{user_id}")
def delete(request, user_id: int):

    delete_user(user_id)

    return {"success": True}