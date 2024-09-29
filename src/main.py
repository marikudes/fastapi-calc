import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, TypedDict

import httpx
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.routers import calc_router


class State(TypedDict):
    http_client: httpx.AsyncClient


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[dict[str, Any], None]:
    # настройка статических файлов
    base_dir = Path(__file__).parent.parent
    static_dir = base_dir.joinpath("src", "static").resolve()
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    # настройка шаблонов
    templates_dir = base_dir.joinpath("src", "templates").resolve()
    app.state.templates = Jinja2Templates(
        directory=templates_dir,
    )  # Сохранение в состояние приложения

    # подключение роутера
    app.include_router(calc_router, prefix="")

    logging.debug("start")

    async with httpx.AsyncClient() as client:
        yield {"http_client": client}

    logging.debug("stop")


# инициализация приложения
app = FastAPI(lifespan=lifespan)

# запуск: uvicorn main:app
