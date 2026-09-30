"""Завдання 2: Багаторівнева система контролю доступу."""

import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
)
from shared.student import STUDENT_NAME, VARIANT_NUMBER


def check_access(
    user_id: str,
    resource_level: int,
    users: dict,
    blocked_users: set,
) -> tuple[str, str]:
    """Реалізує алгоритм перевірки доступу користувача до ресурсу."""
    if user_id not in users:
        return "DENY", "User not found"

    if user_id in blocked_users:
        return "DENY", "User is blocked"

    user_info = users[user_id]
    if not user_info.get("active", False):
        return "DENY", "Account inactive"

    if user_info.get("clearance", 0) >= resource_level:
        return "ALLOW", ""

    return "DENY", "Insufficient clearance"


def run_task2():
    """Основна функція для виконання Завдання 2."""
    print(
        f"\n--- Завдання 2 | Студент: {STUDENT_NAME} "
        f"(Варіант {VARIANT_NUMBER}) ---"
    )

    users = {
        "admin001": {
            "role": "administrator",
            "clearance": 4,
            "department": "IT",
            "active": True,
        },
        "user123": {
            "role": "analyst",
            "clearance": 2,
            "department": "Security",
            "active": True,
        },
        "guest789": {
            "role": "guest",
            "clearance": 1,
            "department": "External",
            "active": True,
        },
        "manager456": {
            "role": "manager",
            "clearance": 3,
            "department": "Operations",
            "active": True,
        },
        "contractor99": {
            "role": "contractor",
            "clearance": 1,
            "department": "External",
            "active": False,
        },
    }

    resources = [
        ("database_backup", 4),
        ("user_logs", 2),
        ("public_docs", 1),
        ("financial_reports", 3),
        ("system_config", 4),
        ("training_materials", 1),
        ("security_policies", 3),
        ("audit_logs", 4),
        ("employee_data", 3),
        ("temp_files", 1),
    ]

    security_levels = ("Public", "Internal", "Confidential", "Secret")
    blocked_users = {"contractor99", "temp_user", "suspended_acc"}

    print("\n[Список ресурсів системи]")
    for res_name, level in resources:
        level_label = security_levels[level - 1]
        print(f" - {res_name:<20}: {level_label} (Level {level})")

    print("\n[Результати перевірки доступу]")
    test_users = list(users.keys()) + ["unknown_usr"]

    for u_id in test_users:
        for res_name, level in resources:
            status, reason = check_access(u_id, level, users, blocked_users)
            reason_fmt = f" ({reason})" if reason else ""
            print(
                f"user={u_id} resource={res_name} "
                f"-> {status}{reason_fmt}"
            )


if __name__ == "__main__":
    run_task2()