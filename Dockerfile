FROM python:3.13-alpine

ARG APP_PORT
ENV APP_PORT=${APP_PORT}

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . /app

RUN python3.13 -m pip --no-cache-dir install --upgrade pip
RUN pip install --no-cache-dir poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-root --no-cache

EXPOSE ${APP_PORT}

CMD poetry run uvicorn main:app --host 0.0.0.0 --port ${APP_PORT}
