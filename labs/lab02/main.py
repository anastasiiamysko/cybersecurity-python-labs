"""Головний модуль запуску утиліти lab02."""

import argparse
import time

from labs.lab02.task1 import Admin, User, UserAccount
from labs.lab02.task2 import run_analyzer, setup_parser as setup_task2_parser


def run_demo() -> None:
    """Демонстрація Завдання 1 (ООП)."""
    print("=== ДЕМОНСТРАЦІЯ ЗАВДАННЯ 1 (ООП) ===\n")

    # 1. Створення користувача
    print("[1] Створення користувача та хешування пароля:")
    user = User(username="alice_sec", email="alice@security.com")
    user.set_password("SuperSecret123!")
    print(f"  Створено: {user}\n")

    # 2. Валідація email
    print("[2] Перевірка валідації email:")
    try:
        user.email = "bad_email_format"
    except ValueError as e:
        print(f"  Успішно перехоплено помилку: {e}")

    user.email = "valid_user@corp.ua"
    print(f"  Оновлений Email: {user.email}\n")

    # 3. Наслідування (Admin)
    print("[3] Демонстрація Admin (Наслідування):")
    admin = Admin(username="admin_bob", email="bob@corp.ua")
    admin.set_password("AdminPass2026!")
    admin.grant_permission("READ_LOGS")
    admin.grant_permission("DELETE_USER")
    print(f"  Адміністратор: {admin}")
    print(f"  Чи має право DELETE_USER? {admin.has_permission('DELETE_USER')}\n")

    # 4. Композиція (UserAccount, Session, AuditLog)
    print("[4] Демонстрація UserAccount та аудиту (Композиція):")
    account = UserAccount(user=user)

    # Невдалий вхід
    account.login(username="alice_sec", password="WrongPassword", ip="192.168.1.50")

    # Успішний вхід
    account.login(username="alice_sec", password="SuperSecret123!", ip="192.168.1.50")
    print(f"  Стан автентифікації: {account.is_authenticated()}")

    # Сесія та таймаут
    session = account["session"]
    if session:
        print(
            f"  Активна сесія з IP {session.ip}, вхід: {session.login_time.strftime('%H:%M:%S')}"
        )

    time.sleep(1)
    print(f"  Чи дійсна сесія через 1 сек? {session.is_active(5)}")

    account.logout()
    print(f"  Після logout(): автентифіковано = {account.is_authenticated()}\n")

    # Вивід логів аудиту
    print("=== Журнал аудиту (AuditLog) ===")
    for record in account["audit_log"].show_all():
        print(
            f"  [{record.timestamp.strftime('%H:%M:%S UTC')}] {record.username:<10} | Дія: {record.action}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Консольна утиліта кібербезпеки (Лабораторна робота №2)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Доступні команди")

    # Додавання команди demo
    subparsers.add_parser("demo", help="Запустити демонстрацію Завдання 1")

    # Додавання команди analyze
    setup_task2_parser(subparsers)

    args = parser.parse_args()

    if args.command == "demo":
        run_demo()
    elif args.command == "analyze":
        run_analyzer(
            log_file=args.log_file,
            output=args.output,
            min_status=args.min_status,
            top_n=args.top,
            out_format=args.format,
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()