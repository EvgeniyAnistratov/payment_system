from pydantic import BaseModel, EmailStr, Field


class UserSchema(BaseModel):
    id: int
    email: EmailStr
    fullname: str
