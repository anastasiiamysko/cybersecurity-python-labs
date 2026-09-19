"""Інформація про автора лабораторних робіт."""


def get_student_data() -> dict:
    return {
        "name": "Мисько Анастасія Андріївна",
        "group": "КБ-205",
        "variant": 16,
    }


if __name__ == "__main__":
    data = get_student_data()
    print(f"Студент: {data['name']}")
    print(f"Група: {data['group']}")
    print(f"Варіант: {data['variant']}")

