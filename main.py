from fastapi import FastAPI
from dishka import make_async_container
from dishka.integrations.fastapi import FastapiProvider, setup_dishka

from payment_system.api.user_api import user_router
from payment_system.core.settings import APP_TITLE, DB_LOGGING, get_db_url
from payment_system.core.app_provider import AppProvider


app = FastAPI(title=APP_TITLE)
app.include_router(user_router)
container = make_async_container(
    AppProvider(get_db_url(), DB_LOGGING),
    FastapiProvider()
)
setup_dishka(container, app)

@app.get("/")
async def main():
    return APP_TITLE