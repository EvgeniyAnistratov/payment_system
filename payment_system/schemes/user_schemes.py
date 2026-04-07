from pydantic import BaseModel, EmailStr


class UserScheme(BaseModel):
    id: int
    email: EmailStr
    fullname: str
