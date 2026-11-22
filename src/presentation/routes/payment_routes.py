from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Response, status

from src.application.use_cases.payments.process_payment import ProcessPaymentUseCase
from src.presentation.schemas.payment import ProcessPaymentRequest

payment_router = APIRouter(
    route_class=DishkaRoute,
    prefix="/transactions",
    tags=["transactions"],
)


@payment_router.post("")
async def process_transaction(
    body: ProcessPaymentRequest,
    use_case: FromDishka[ProcessPaymentUseCase],
) -> Response:
    await use_case.execute(body.to_input())
    return Response(status_code=status.HTTP_201_CREATED)
