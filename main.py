from fastapi import FastAPI

from payment_system.settings import APP_TITLE


app = FastAPI(title=APP_TITLE)


@app.get("/")
async def main():
    return APP_TITLE