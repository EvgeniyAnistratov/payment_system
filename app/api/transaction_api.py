from fastapi import APIRouter
from dishka.integrations.fastapi import DishkaRoute, FromDishka

from app.schemas import NewTransactionSchema
from app.services import TransactionService


transaction_router = APIRouter(route_class=DishkaRoute, prefix="/transactions", tags=["transactions"])


@transaction_router.post("")
async def process_transaction(
    transaction: NewTransactionSchema,
    service: FromDishka[TransactionService]
):
    return await service.process_transaction(transaction)
