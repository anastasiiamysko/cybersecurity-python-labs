"""Скрипт початкового заповнення бази даних з JSON."""

import json
import sqlite3
from contextlib import closing

from labs.lab03.database import BASE_DIR, get_connection, initialize_database

SEED_PATH = BASE_DIR / "data" / "seed.json"


def seed_database() -> None:
    """Заповнити порожню базу початковими даними в одній транзакції."""
    initialize_database()

    with closing(get_connection()) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM categories")
        if cursor.fetchone()[0] > 0:
            print("База даних вже містить дані. Заповнення скасовано.")
            return

        if not SEED_PATH.exists():
            print(f"Файл початкових даних {SEED_PATH} не знайдено.")
            return

        with open(SEED_PATH, encoding="utf-8") as f:
            data = json.load(f)

        try:
            with connection:
                connection.executemany(
                    "INSERT INTO categories (id, name) VALUES (?, ?)",
                    [(cat["id"], cat["name"]) for cat in data["categories"]],
                )
                connection.executemany(
                    """
                    INSERT INTO records (code, title, category_id, value, status)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    [
                        (
                            rec["code"],
                            rec["title"],
                            rec["category_id"],
                            rec["value"],
                            rec["status"],
                        )
                        for rec in data["records"]
                    ],
                )
            print("Базу даних успішно заповнено початковими даними.")
        except sqlite3.Error as e:
            print(f"Помилка заповнення бази: {e}. Зміни скасовано.")


if __name__ == "__main__":
    seed_database()
