import hashlib
import sys
from pathlib import Path

# Додаємо кореневу папку проєкту для імпорту модуля shared
sys.path.append(str(Path(__file__).resolve().parent.parent))

from shared.student import get_student_data


def generate_hash(text: str, salt: str = "") -> dict:
    """Хешування даних з використанням алгоритмів MD5 та SHA-256."""
    salted_text = (text + salt).encode("utf-8")
    return {
        "md5": hashlib.md5(salted_text).hexdigest(),
        "sha256": hashlib.sha256(salted_text).hexdigest(),
    }


def main():
    student = get_student_data()
    print("=" * 50)
    print("Лабораторна робота №1 | Завдання 2")
    print(f"Виконав(ла): {student['name']}")
    print(f"Група: {student['group']} | Варіант: {student['variant']}")
    print("=" * 50)

    secret_message = f"Cybersecurity_Lab1_Variant_{student['variant']}"
    salt_value = f"Salt_Group_{student['group']}"

    hashes = generate_hash(secret_message, salt=salt_value)

    print(f"\nВхідне повідомлення: {secret_message}")
    print(f"Сіль (Salt):         {salt_value}")
    print(f"MD5 хеш:             {hashes['md5']}")
    print(f"SHA-256 хеш:         {hashes['sha256']}")


if __name__ == "__main__":
    main()