import sys
from pathlib import Path


sys.path.append(str(Path(__file__).resolve().parent.parent))

from shared.student import get_student_data


def process_text(text: str, shift: int = 3) -> str:
    """Проста обробка та кодування тексту за правилом варіанта."""
    result = []
    for char in text:
        if char.isalpha():
            # Зсув символу в межах ASCII
            start = ord('a') if char.islower() else ord('A')
            new_char = chr((ord(char) - start + shift) % 26 + start)
            result.append(new_char)
        else:
            result.append(char)
    return "".join(result)


def main():
    student = get_student_data()
    print("=" * 50)
    print(f"Лабораторна робота №1 | Завдання 1")
    print(f"Виконав(ла): {student['name']}")
    print(f"Група: {student['group']} | Варіант: {student['variant']}")
    print("=" * 50)

    sample_text = "Cybersecurity Python Lab 1"
    processed = process_text(sample_text, shift=student['variant'])

    print(f"\nВхідний текст: {sample_text}")
    print(f"Зашифрований текст (зсув {student['variant']}): {processed}")


if __name__ == "__main__":
    main()