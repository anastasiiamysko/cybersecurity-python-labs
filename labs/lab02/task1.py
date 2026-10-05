"""Модуль Завдання 1: Класи User, Admin, Session, AuditLog та UserAccount."""

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import os
import re
from typing import Any, Optional

PBKDF2_ITERATIONS = 100_000
HASH_NAME = "sha256"


class User:
    """Клас користувача з валідацією email та безпечним хешуванням пароля."""

    def __init__(
        self, username: str, email: str, role: str = "user", active: bool = True
    ) -> None:
        self.username: str = username
        self.role: str = role
        self.active: bool = active
        self._email: str = ""
        self.email = email  # Викликає setter з валідацією

        self.__password_hash: bytes = b""
        self.__password_salt: bytes = b""

    @property
    def email(self) -> str:
        """Getter для атрибута email."""
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        """Setter для email з перевіркою формату за допомогою регулярного виразу."""
        pattern = r"^[a-zA-Z][a-zA-Z0-9_]{2,63}@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, value):
            raise ValueError(f"Некоректний формат email адреси: '{value}'")
        self._email = value

    def set_password(self, password: str) -> None:
        """Зберігає хеш пароля PBKDF2 з використанням випадкової солі."""
        if not password:
            raise ValueError("Пароль не може бути порожнім.")
        self.__password_salt = os.urandom(16)
        self.__password_hash = hashlib.pbkdf2_hmac(
            HASH_NAME,
            password.encode("utf-8"),
            self.__password_salt,
            PBKDF2_ITERATIONS,
        )

    def check_password(self, password: str) -> bool:
        """Перевіряє правильність пароля за допомогою hmac.compare_digest."""
        if not self.__password_hash or not self.__password_salt:
            return False
        calculated_hash = hashlib.pbkdf2_hmac(
            HASH_NAME,
            password.encode("utf-8"),
            self.__password_salt,
            PBKDF2_ITERATIONS,
        )
        return hmac.compare_digest(calculated_hash, self.__password_hash)

    def deactivate(self) -> None:
        """Деактивує обліковий запис."""
        self.active = False

    def __str__(self) -> str:
        status = "Active" if self.active else "Inactive"
        return f"User({self.username}, Email: {self.email}, Role: {self.role}, Status: {status})"


class Admin(User):
    """Клас Адміністратора (наслідує User та додає управління правами)."""

    def __init__(
        self,
        username: str,
        email: str,
        permissions: Optional[set[str]] = None,
        active: bool = True,
    ) -> None:
        super().__init__(username=username, email=email, role="admin", active=active)
        self.permissions: set[str] = set(permissions) if permissions else set()

    def grant_permission(self, permission: str) -> None:
        """Надає новий дозвіл."""
        self.permissions.add(permission)

    def revoke_permission(self, permission: str) -> None:
        """Скасовує дозвіл."""
        self.permissions.discard(permission)

    def has_permission(self, permission: str) -> bool:
        """Перевіряє наявність дозволу."""
        return permission in self.permissions

    def __str__(self) -> str:
        base_str = super().__str__()
        perms = ", ".join(sorted(self.permissions)) if self.permissions else "None"
        return f"{base_str} | Permissions: [{perms}]"


class Session:
    """Відстежує сеанс користувача та його активність."""

    def __init__(self, ip: str) -> None:
        self.ip: str = ip
        now = datetime.now(timezone.utc)
        self.login_time: datetime = now
        self.last_activity: datetime = now

    def touch(self) -> None:
        """Оновлює час останньої активності."""
        self.last_activity = datetime.now(timezone.utc)

    def is_active(self, timeout_sec: int) -> bool:
        """Перевіряє, чи активна сесія (порівняно з таймаутом)."""
        if timeout_sec <= 0:
            raise ValueError("Таймаут повинен бути додатним числом.")
        elapsed = (datetime.now(timezone.utc) - self.last_activity).total_seconds()
        return elapsed <= timeout_sec


@dataclass
class AuditRecord:
    """Запис у журналі аудиту."""

    timestamp: datetime
    username: str
    action: str


class AuditLog:
    """Журнал подій аудиту."""

    def __init__(self) -> None:
        self.records: list[AuditRecord] = []

    def add_log(self, username: str, action: str) -> None:
        """Додає подію до аудиту."""
        record = AuditRecord(
            timestamp=datetime.now(timezone.utc),
            username=username,
            action=action,
        )
        self.records.append(record)

    def show_all(self) -> list[AuditRecord]:
        """Повертає список всіх записів аудиту."""
        return self.records


SESSION_TIMEOUT_SEC = 900


class UserAccount:
    """Обліковий запис (Композиція User, Session та AuditLog)."""

    def __init__(self, user: User, audit_log: Optional[AuditLog] = None) -> None:
        self.user: User = user
        self.session: Optional[Session] = None
        self.audit_log: AuditLog = audit_log if audit_log is not None else AuditLog()

    def login(self, username: str, password: str, ip: str) -> bool:
        """Авторизує користувача та створює сесію."""
        if username != self.user.username or not self.user.active:
            self.audit_log.add_log(username, "login_failure")
            return False

        if not self.user.check_password(password):
            self.audit_log.add_log(username, "login_failure")
            return False

        self.session = Session(ip)
        self.session.touch()
        self.audit_log.add_log(username, "login_success")
        return True

    def is_authenticated(self) -> bool:
        """Перевіряє наявність діючої сесії."""
        if self.session is None:
            return False
        return self.session.is_active(SESSION_TIMEOUT_SEC)

    def logout(self) -> None:
        """Завершує сесію та фіксує вихід."""
        if self.session is not None:
            self.audit_log.add_log(self.user.username, "logout")
            self.session = None

    def __getitem__(self, key: str) -> Any:
        """Отримання доступу за ключем."""
        allowed_keys = {
            "user": self.user,
            "session": self.session,
            "audit_log": self.audit_log,
        }
        if key not in allowed_keys:
            raise KeyError(f"Ключ '{key}' не існує або приватний.")
        return allowed_keys[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Запис атрибута за ключем з перевіркою типів."""
        if key == "user":
            if not isinstance(value, User):
                raise TypeError("Значення має бути об'єктом User.")
            self.user = value
        elif key == "session":
            if value is not None and not isinstance(value, Session):
                raise TypeError("Значення має бути Session або None.")
            self.session = value
        elif key == "audit_log":
            if not isinstance(value, AuditLog):
                raise TypeError("Значення має бути AuditLog.")
            self.audit_log = value
        else:
            raise KeyError(f"Заборонено змінювати ключ '{key}'.")