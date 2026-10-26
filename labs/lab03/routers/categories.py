"""Маршрути для управління категоріями."""

import sqlite3

from fastapi import APIRouter, HTTPException, Path, status

from labs.lab03.repository import DBRepository
from labs.lab03.schemas import CategoryCreate, CategoryRead

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=list[CategoryRead])
def list_categories() -> list[CategoryRead]:
    return [CategoryRead(**cat) for cat in DBRepository.get_categories()]


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate) -> CategoryRead:
    try:
        cat_dict = DBRepository.create_category(payload.name)
        return CategoryRead(**cat_dict)
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Категорія з такою назвою вже існує",
        )


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int = Path(..., gt=0)) -> None:
    res = DBRepository.delete_category(category_id)
    if res == "not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категорію не знайдено",
        )
    if res == "has_records":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Неможливо видалити категорію, що містить записи",
        )
