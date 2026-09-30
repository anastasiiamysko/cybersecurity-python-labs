"""Головний модуль запуску Лабораторної роботи №1."""

import os
import sys

# Налаштування шляху для коректного імпорту спільних модулів (shared)
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
)

from labs.lab01 import task1, task2, task3


def main() -> None:
    """Запускає всі завдання лабораторної роботи."""
    print("\n" + "=" * 60)
    print("      ЗАПУСК ЛАБОРАТОРНОЇ РОБОТИ №1")
    print("=" * 60 + "\n")

    # Запуск Завдання 1
    if hasattr(task1, "run_task1"):
        task1.run_task1()
    elif hasattr(task1, "main"):
        task1.main()
    elif hasattr(task1, "run"):
        task1.run()

    print("\n" + "-" * 60 + "\n")

    # Запуск Завдання 2
    if hasattr(task2, "run_task2"):
        task2.run_task2()
    elif hasattr(task2, "main"):
        task2.main()
    elif hasattr(task2, "run"):
        task2.run()

    print("\n" + "-" * 60 + "\n")

    # Запуск Завдання 3
    if hasattr(task3, "run_task3"):
        task3.run_task3()
    elif hasattr(task3, "main"):
        task3.main()
    elif hasattr(task3, "run"):
        task3.run()

    print("\n" + "=" * 60)
    print("      УСІ ЗАВДАННЯ УСПІШНО ВИКОНАНО")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()