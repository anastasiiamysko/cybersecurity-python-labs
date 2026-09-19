import base64
import json
import sys
from pathlib import Path

# Додаємо кореневу папку проєкту для імпорту модуля shared
sys.path.append(str(Path(__file__).resolve().parent.parent))

from shared.student import get_student_data


def encode_data(data: str) -> str:
    """Кодування рядка у формат Base64."""
    encoded_bytes = base64.b64encode(data.encode("utf-8"))
    return encoded_bytes.decode("utf-8")


def decode_data(encoded_str: str) -> str:
    """Декодування рядка з формату Base64."""
    decoded_bytes = base64.b64decode(encoded_str.encode("utf-8"))
    return decoded_bytes.decode("utf-8")


def main():
    student = get_student_data()
    print("=" * 50)
    print("Лабораторна робота №1 | Завдання 3")
    print(f"Виконав(ла): {student['name']}")
    print(f"Група: {student['group']} | Варіант: {student['variant']}")
    print("=" * 50)

    payload = {
        "student": student['name'],
        "group": student['group'],
        "variant": student['variant'],
        "status": "Lab 1 Completed"
    }

    json_str = json.dumps(payload, ensure_ascii=False)
    encoded_payload = encode_data(json_str)
    decoded_payload = decode_data(encoded_payload)

    print(f"\nОригінальні дані (JSON): {json_str}")
    print(f"Закодовані дані (Base64): {encoded_payload}")
    print(f"Декодовані дані:         {decoded_payload}")


if __name__ == "__main__":
    main()