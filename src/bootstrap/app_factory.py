from dishka import make_async_container
from dishka.integrations.fastapi import FastapiProvider, setup_dishka
from fastapi import FastAPI

from src.bootstrap.providers import (
    AdapterProvider,
    ConfigProvider,
    DatabaseProvider,
    UseCaseProvider,
)
from src.presentation.error_handlers import register_error_handlers
from src.presentation.routes import auth_router, payment_router, user_router


def create_app() -> FastAPI:
    app = FastAPI(title="Payment system", root_path="/api")
    app.include_router(auth_router)
    app.include_router(user_router)
    app.include_router(payment_router)
    register_error_handlers(app)

    container = make_async_container(
        ConfigProvider(),
        DatabaseProvider(),
        AdapterProvider(),
        UseCaseProvider(),
        FastapiProvider(),
    )
    setup_dishka(container, app)
    return app
