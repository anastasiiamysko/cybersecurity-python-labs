"""Головний модуль FastAPI-застосунку ЛР №3."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI

from labs.lab03.config import DOMAIN_NAME, THRESHOLD, UNIT
from labs.lab03.database import initialize_database
from labs.lab03.routers.categories import router as categories_router
from labs.lab03.routers.records import router as records_router
from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    initialize_database()
    yield


app = FastAPI(
    title=DOMAIN_NAME,
    description=(
        f"Web API для обліку вразливостей. Одиниця вимірювання value: {UNIT}. "
        f"Поріг небезпеки: {THRESHOLD}."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(categories_router)
app.include_router(records_router)


@app.get("/ping", tags=["System"])
def ping() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/student", tags=["System"])
def get_student() -> dict[str, Any]:
    return {
        "student_name": STUDENT_NAME,
        "group_name": GROUP_NAME,
        "variant_number": VARIANT_NUMBER,
    }
