from ninja import Schema


class UserCreateSchema(Schema):
    username: str
    email: str
    password: str


class UserUpdateSchema(Schema):
    username: str
    email: str


class UserResponseSchema(Schema):
    id: int
    username: str
    email: str
    is_active: bool