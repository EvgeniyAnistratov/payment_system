from fastapi import APIRouter
from dishka.integrations.fastapi import DishkaRoute, FromDishka

from payment_system.schemas.user import UserSchema
from payment_system.services.user_service import UserService


user_router = APIRouter(route_class=DishkaRoute, prefix="/users", tags=["users"])


@user_router.get("/{user_id}", response_model=UserSchema)
async def read_user_info(user_id: int, user_service: FromDishka[UserService]):
    return await user_service.get_user(user_id)
