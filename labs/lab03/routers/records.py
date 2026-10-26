"""Маршрути для управління записами."""

from typing import Literal

from fastapi import APIRouter, HTTPException, Path, Query, status

from labs.lab03.config import VALUE_MAX, VALUE_MIN
from labs.lab03.repository import DBRepository
from labs.lab03.schemas import RecordCreate, RecordRead, RecordReplace

router = APIRouter(prefix="/records", tags=["Records"])


@router.get("", response_model=list[RecordRead])
def list_records(
    category_id: int | None = Query(None, gt=0),
    status_filter: Literal["new", "in_progress", "done"] | None = Query(
        None, alias="status"
    ),
    min_value: float | None = Query(None, ge=VALUE_MIN, le=VALUE_MAX),
    q: str | None = Query(None, min_length=1, max_length=120),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> list[RecordRead]:
    records = DBRepository.get_records(
        category_id=category_id,
        status=status_filter,
        min_value=min_value,
        q=q,
        limit=limit,
        offset=offset,
    )
    return [RecordRead(**r) for r in records]


@router.get("/{record_id}", response_model=RecordRead)
def get_record(record_id: int = Path(..., gt=0)) -> RecordRead:
    rec = DBRepository.get_record_by_id(record_id)
    if not rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запис не знайдено",
        )
    return RecordRead(**rec)


@router.post("", response_model=RecordRead, status_code=status.HTTP_201_CREATED)
def create_record(payload: RecordCreate) -> RecordRead:
    rec, status_code = DBRepository.create_record(payload.model_dump())
    if status_code == "category_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категорію не знайдено",
        )
    if status_code == "duplicate_code":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Запис із таким кодом вже існує",
        )
    return RecordRead(**rec)


@router.put("/{record_id}", response_model=RecordRead)
def update_record(
    payload: RecordReplace, record_id: int = Path(..., gt=0)
) -> RecordRead:
    rec, status_code = DBRepository.replace_record(record_id, payload.model_dump())
    if status_code == "record_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запис не знайдено",
        )
    if status_code == "category_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Вказану категорію не знайдено",
        )
    if status_code == "duplicate_code":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Запис із таким кодом вже існує",
        )
    return RecordRead(**rec)


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(record_id: int = Path(..., gt=0)) -> None:
    if not DBRepository.delete_record(record_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запис не знайдено",
        )


@router.post(
    "/bulk", response_model=list[RecordRead], status_code=status.HTTP_201_CREATED
)
def bulk_create_records(payload: list[RecordCreate]) -> list[RecordRead]:
    if not (1 <= len(payload) <= 100):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Розмір пакета має бути від 1 до 100 елементів",
        )

    records_data = [item.model_dump() for item in payload]
    results, err = DBRepository.bulk_create_records(records_data)

    if err == "duplicate_code_in_bulk":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пакет містить дублікати коду всередині масиву",
        )
    if err == "category_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Один із записів посилається на неіснуючу категорію",
        )
    if err == "duplicate_code_in_db":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Один із записів порушує унікальність коду в базі даних",
        )

    return [RecordRead(**r) for r in results]
