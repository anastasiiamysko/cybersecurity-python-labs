"""Модуль виконання параметризованих SQL-запитів до SQLite."""

import sqlite3
from contextlib import closing
from typing import Any

from labs.lab03.database import get_connection


class DBRepository:
    # --- Операції з категоріями ---
    @staticmethod
    def get_categories() -> list[dict[str, Any]]:
        with closing(get_connection()) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT id, name FROM categories ORDER BY id ASC"
            ).fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def create_category(name: str) -> dict[str, Any]:
        with closing(get_connection()) as conn:
            with conn:
                cursor = conn.execute(
                    "INSERT INTO categories (name) VALUES (?)", (name,)
                )
                cat_id = cursor.lastrowid
            return {"id": cat_id, "name": name}

    @staticmethod
    def delete_category(category_id: int) -> str:
        with closing(get_connection()) as conn:
            conn.row_factory = sqlite3.Row
            cat = conn.execute(
                "SELECT id FROM categories WHERE id = ?", (category_id,)
            ).fetchone()
            if not cat:
                return "not_found"

            records_count = conn.execute(
                "SELECT COUNT(*) FROM records WHERE category_id = ?", (category_id,)
            ).fetchone()[0]
            if records_count > 0:
                return "has_records"

            with conn:
                conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
            return "success"

    # --- Операції із записами ---
    @staticmethod
    def get_records(
        category_id: int | None = None,
        status: str | None = None,
        min_value: float | None = None,
        q: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        with closing(get_connection()) as conn:
            conn.row_factory = sqlite3.Row
            query = """
                SELECT r.id, r.code, r.title, r.category_id, c.name AS category_name,
                       r.value, r.status
                FROM records r
                JOIN categories c ON r.category_id = c.id
                WHERE 1=1
            """
            params: list[Any] = []

            if category_id is not None:
                query += " AND r.category_id = ?"
                params.append(category_id)
            if status is not None:
                query += " AND r.status = ?"
                params.append(status)
            if min_value is not None:
                query += " AND r.value >= ?"
                params.append(min_value)
            if q is not None:
                query += " AND instr(r.title, ?) > 0"
                params.append(q)

            query += " ORDER BY r.id ASC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def get_record_by_id(record_id: int) -> dict[str, Any] | None:
        with closing(get_connection()) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                """
                SELECT r.id, r.code, r.title, r.category_id, c.name AS category_name,
                       r.value, r.status
                FROM records r
                JOIN categories c ON r.category_id = c.id
                WHERE r.id = ?
                """,
                (record_id,),
            ).fetchone()
            return dict(row) if row else None

    @staticmethod
    def create_record(data: dict[str, Any]) -> tuple[dict[str, Any] | None, str]:
        with closing(get_connection()) as conn:
            cat = conn.execute(
                "SELECT name FROM categories WHERE id = ?", (data["category_id"],)
            ).fetchone()
            if not cat:
                return None, "category_not_found"

            try:
                with conn:
                    cursor = conn.execute(
                        """
                        INSERT INTO records (code, title, category_id, value, status)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            data["code"],
                            data["title"],
                            data["category_id"],
                            data["value"],
                            data["status"],
                        ),
                    )
                    rec_id = cursor.lastrowid
                return DBRepository.get_record_by_id(rec_id), "success"
            except sqlite3.IntegrityError:
                return None, "duplicate_code"

    @staticmethod
    def replace_record(
        record_id: int, data: dict[str, Any]
    ) -> tuple[dict[str, Any] | None, str]:
        with closing(get_connection()) as conn:
            existing = conn.execute(
                "SELECT id FROM records WHERE id = ?", (record_id,)
            ).fetchone()
            if not existing:
                return None, "record_not_found"

            cat = conn.execute(
                "SELECT id FROM categories WHERE id = ?", (data["category_id"],)
            ).fetchone()
            if not cat:
                return None, "category_not_found"

            try:
                with conn:
                    conn.execute(
                        """
                        UPDATE records
                        SET code = ?, title = ?, category_id = ?, value = ?, status = ?
                        WHERE id = ?
                        """,
                        (
                            data["code"],
                            data["title"],
                            data["category_id"],
                            data["value"],
                            data["status"],
                            record_id,
                        ),
                    )
                return DBRepository.get_record_by_id(record_id), "success"
            except sqlite3.IntegrityError:
                return None, "duplicate_code"

    @staticmethod
    def delete_record(record_id: int) -> bool:
        with closing(get_connection()) as conn, conn:
            cursor = conn.execute("DELETE FROM records WHERE id = ?", (record_id,))
            return cursor.rowcount > 0

    @staticmethod
    def bulk_create_records(
        records_data: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]] | None, str]:
        with closing(get_connection()) as conn:
            # 1. Перевірка внутрішніх дублікатів коду у пакеті
            codes = [r["code"] for r in records_data]
            if len(codes) != len(set(codes)):
                return None, "duplicate_code_in_bulk"

            # 2. Перевірка наявності всіх категорій
            category_ids = {r["category_id"] for r in records_data}
            placeholders = ",".join("?" for _ in category_ids)
            existing_cats = conn.execute(
                f"SELECT id FROM categories WHERE id IN ({placeholders})",
                tuple(category_ids),
            ).fetchall()
            if len(existing_cats) != len(category_ids):
                return None, "category_not_found"

            # 3. Атомарне вставлення пакету в одній транзакції
            inserted_ids = []
            try:
                with conn:
                    for rec in records_data:
                        cursor = conn.execute(
                            """
                            INSERT INTO records (code, title, category_id, value, status)
                            VALUES (?, ?, ?, ?, ?)
                            """,
                            (
                                rec["code"],
                                rec["title"],
                                rec["category_id"],
                                rec["value"],
                                rec["status"],
                            ),
                        )
                        inserted_ids.append(cursor.lastrowid)
            except sqlite3.IntegrityError:
                return None, "duplicate_code_in_db"

            result = []
            for r_id in inserted_ids:
                row = DBRepository.get_record_by_id(r_id)
                if row:
                    result.append(row)
            return result, "success"
