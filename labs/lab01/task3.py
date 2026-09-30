"""Завдання 3: Безпечне хешування, CSV-база та JSON-логування з винятками."""

import csv
import datetime
import hashlib
import json
import os
import sys
from functools import wraps

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
)
from shared.student import STUDENT_NAME, VARIANT_NUMBER


class ValidationError(Exception):
    """Кастомний виняток для помилок валідації пароля."""



HASH_ALG = "sha3_512"
MIN_PASS_LEN = 12
PERSONAL_SALT = str(VARIANT_NUMBER).zfill(5)

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))
USERS_CSV_PATH = os.path.join(DATA_DIR, "users.csv")
LOG_JSON_PATH = os.path.join(DATA_DIR, "log.json")


def generate_hash(password: str, salt: str = "00000") -> str:
    """Генерує хеш від конкатенації пароля та солі."""
    if not password or not salt:
        raise ValueError("Пароль та сіль не можуть бути порожніми!")

    if len(password) < MIN_PASS_LEN:
        raise ValidationError(
            f"Пароль коротший за {MIN_PASS_LEN} символів!"
        )

    salted_data = (password + salt).encode("utf-8")
    hasher = hashlib.new(HASH_ALG)
    hasher.update(salted_data)
    return hasher.hexdigest()


def log_event(func):
    """Декоратор для логування спроб входу у файл log.json."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        username = "unknown"
        if args:
            username = args[0]
        elif "username" in kwargs:
            username = kwargs["username"]

        result = "failure"
        try:
            res = func(*args, **kwargs)
            result = "success" if res else "failure"
            return res
        except Exception as e:
            result = f"failure ({type(e).__name__})"
            raise e
        finally:
            log_data = {
                "event": "login",
                "user": username,
                "result": result,
                "timestamp": datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "args": list(args),
                "kwargs": kwargs,
            }

            os.makedirs(DATA_DIR, exist_ok=True)
            logs = []
            if os.path.exists(LOG_JSON_PATH):
                try:
                    with open(LOG_JSON_PATH, "r", encoding="utf-8") as f:
                        logs = json.load(f)
                except (OSError, json.JSONDecodeError):
                    logs = []

            logs.append(log_data)
            with open(LOG_JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(logs, f, ensure_ascii=False, indent=4)

    return wrapper


def create_user(username: str, password: str) -> tuple[str, str]:
    """Створює кортеж (username, hash_value)."""
    h_val = generate_hash(password, salt=PERSONAL_SALT)
    return username, h_val


def create_users(users_list: tuple):
    """Створює CSV-базу даних користувачів."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(USERS_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["username", "password_hash"])
        for u_name, pwd in users_list:
            try:
                row = create_user(u_name, pwd)
                writer.writerow(row)
            except (ValueError, ValidationError) as err:
                print(f"[Помилка реєстрації {u_name}]: {err}")


def read_users_db() -> list[dict]:
    """Зчитує користувачів з CSV-файлу."""
    if not os.path.exists(USERS_CSV_PATH):
        raise FileNotFoundError(f"Файл {USERS_CSV_PATH} не знайдено.")

    users_db = []
    with open(USERS_CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            users_db.append(row)
    return users_db


@log_event
def login(username: str, password: str) -> bool:
    """Автентифікує користувача за логіном і паролем."""
    if not username or not password:
        raise ValueError("Логін та пароль не можуть бути порожніми!")

    users_db = read_users_db()
    for row in users_db:
        if row["username"] == username:
            try:
                calc_hash = generate_hash(password, salt=PERSONAL_SALT)
                return calc_hash == row["password_hash"]
            except ValidationError:
                return False
    return False


def run_task3():
    """Основна функція для виконання Завдання 3."""
    print(
        f"\n--- Завдання 3 | Студент: {STUDENT_NAME} "
        f"(Варіант {VARIANT_NUMBER}) ---"
    )

    users_to_register = (
        ("admin_user", "SuperSecret123!"),
        ("analyst_sec", "Analysis#2023Pass"),
        ("operator01", "OpPass12345678!"),
        ("manager_key", "ManagerPass#999"),
        ("auditor_01", "AuditSecure2023!"),
        ("guest_user1", "GuestPass123456"),
        ("tech_support", "TechSupport#2023"),
        ("dev_backend", "BackendDev#2023"),
        ("sys_engineer", "SysEngineer!2023"),
        ("security_lead", "SecLeadPass#2023"),
    )

    try:
        print("[1] Створення бази користувачів users.csv...")
        create_users(users_to_register)

        print("\n[2] Зчитана база даних:")
        db_content = read_users_db()
        print(f"{'Логін':<16} | {'Хеш (SHA3-512)':<60}")
        print("-" * 79)
        for user in db_content:
            print(f"{user['username']:<16} | {user['password_hash'][:57]}...")

        print("\n[3] Тестування автентифікації:")
        ok_login = login("admin_user", "SuperSecret123!")
        print(f"Вхід admin_user (правильний): {ok_login}")

        bad_pass = login("admin_user", "WrongPassword123!")
        print(f"Вхід admin_user (неправильний пароль): {bad_pass}")

        bad_user = login("unknown_user", "SuperSecret123!")
        print(f"Вхід unknown_user: {bad_user}")

    except (OSError, FileNotFoundError, PermissionError) as e:
        print(f"[Помилка файлової системи]: {e}")
    except ValidationError as e:
        print(f"[Помилка валідації]: {e}")
    except ValueError as e:
        print(f"[Помилка значення]: {e}")


if __name__ == "__main__":
    run_task3()