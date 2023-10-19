from pydantic import BaseModel


class UserCreateRequest(BaseModel):
    username: str
    email: str
    password: str


class UserEditRequest(UserCreateRequest):
    email: None
    password: None