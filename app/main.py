from fastapi import FastAPI
from dishka import make_async_container
from dishka.integrations.fastapi import FastapiProvider, setup_dishka
from dotenv import load_dotenv

load_dotenv()

from app.api import auth_router, user_router, transaction_router
from app.core.settings import APP_TITLE, DB_LOGGING, get_db_url
from app.core.app_provider import AppProvider


app = FastAPI(title=APP_TITLE, root_path="/api")
app.include_router(auth_router)
app.include_router(transaction_router)
app.include_router(user_router)

container = make_async_container(
    AppProvider(get_db_url(), DB_LOGGING),
    FastapiProvider()
)
setup_dishka(container, app)

@app.get("/")
async def main():
    return APP_TITLE
