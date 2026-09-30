"""Завдання 1: Комплексний аналізатор надійності паролів."""

import os
import random
import sys
from collections import Counter

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
)
from shared.student import STUDENT_NAME, VARIANT_NUMBER


def analyze_password_strength(
    password: str, criteria: dict, forbidden: set, pass_counts: dict
) -> str:
    """Оцінює надійність пароля за заданим алгоритмом."""
    min_len = criteria["min_length"]
    pwd_lower = password.lower()

    if pwd_lower in forbidden or len(password) < min_len:
        return "Заборонений"

    has_digit = any(c.isdigit() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_special = any(not c.isalnum() for c in password)

    req_digit = criteria.get("require_digits", False)
    req_upper = criteria.get("require_upper", False)
    req_special = criteria.get("require_special", False)

    digit_ok = not req_digit or has_digit
    upper_ok = not req_upper or has_upper
    special_ok = not req_special or has_special

    satisfies_all = (
        digit_ok and upper_ok and special_ok and has_lower
    )
    is_unique = pass_counts.get(password, 0) == 1

    if satisfies_all:
        if len(password) >= min_len + 4 and is_unique:
            return "Дуже сильний"
        return "Сильний"

    meets_some = (
        (has_digit and req_digit)
        or (has_upper and req_upper)
        or (has_special and req_special)
        or has_lower
    )
    if len(password) >= min_len and meets_some:
        return "Середній"

    return "Слабкий"


def run_task1():
    """Основна функція для виконання Завдання 1."""
    print(
        f"--- Завдання 1 | Студент: {STUDENT_NAME} "
        f"(Варіант {VARIANT_NUMBER}) ---"
    )

    passwords = [
        "password123",
        "Qwerty!2023",
        "admin",
        "MyP@ssword",
        "123456",
        "SecurePass!",
        "test",
        "P@ssword123",
        "welcome",
        "StrongP@ss1",
    ]
    criteria = {
        "min_length": 8,
        "require_digits": True,
        "require_upper": True,
        "require_special": True,
    }
    forbidden_passwords = {
        "password",
        "123456",
        "admin",
        "test",
        "welcome",
        "qwerty",
    }

    random_indices = [
        random.randint(0, len(passwords) - 1) for _ in range(3)
    ]
    duplicates = [passwords[i] for i in random_indices]
    passwords.extend(duplicates)

    pass_counts = Counter(passwords)

    print(
        f"{'№':<4} | {'Пароль':<18} | {'Довжина':<8} | "
        f"{'Статус надійності':<15}"
    )
    print("-" * 55)

    for idx, pwd in enumerate(passwords, 1):
        status = analyze_password_strength(
            pwd, criteria, forbidden_passwords, pass_counts
        )
        print(f"{idx:<4} | {pwd:<18} | {len(pwd):<8} | {status}")


if __name__ == "__main__":
    run_task1()