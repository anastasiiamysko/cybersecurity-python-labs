"""Завдання 2 (Варіант 1): Аналізатор журналів веб-сервера (Nginx/Apache Access Log)."""

import argparse
from collections import Counter, defaultdict
import csv
from dataclasses import dataclass
from datetime import datetime
import json
import logging
from pathlib import Path
import re
from typing import Any, Optional

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

# Регулярний вираз для розбору рядків access.log (Combined Log Format)
LOG_PATTERN = re.compile(
    r'^(?P<ip>\S+)\s+\S+\s+\S+\s+\[(?P<time>[^\]]+)\]\s+"(?P<method>\S+)\s+(?P<uri>\S+)\s+HTTP/[0-9.]+"\s+(?P<status>\d{3})\s+(?P<bytes>\S+)'
)

# Сигнатури базових атак (SQLi, Directory Traversal, XSS)
ATTACK_PATTERNS = {
    "SQLi": re.compile(
        r"(?i)(UNION\s+SELECT|SELECT.*FROM|' OR '1'='1|--|;|\bDROP\b)"
    ),
    "Directory Traversal": re.compile(r"(\.\./|\.\.\\)"),
    "XSS": re.compile(r"(?i)(<script|javascript:|onerror=|onload=)"),
}


@dataclass
class LogEntry:
    """Структура для розібраного запису з логу."""

    ip: str
    timestamp: datetime
    method: str
    uri: str
    status: int
    bytes_sent: int


def parse_log_line(line: str) -> Optional[LogEntry]:
    """Розбирає рядок логу за допомогою регулярного виразу."""
    match = LOG_PATTERN.match(line.strip())
    if not match:
        return None

    data = match.groupdict()
    try:
        # Формат дати: 27/Sep/2026:08:00:00 +0000
        time_part = data["time"].split()[0]
        dt = datetime.strptime(time_part, "%d/%b/%Y:%H:%M:%S")
        bytes_sent = int(data["bytes"]) if data["bytes"].isdigit() else 0

        return LogEntry(
            ip=data["ip"],
            timestamp=dt,
            method=data["method"],
            uri=data["uri"],
            status=int(data["status"]),
            bytes_sent=bytes_sent,
        )
    except Exception:
        return None


def run_analyzer(
    log_file: str,
    output: str,
    min_status: int = 400,
    top_n: int = 5,
    out_format: str = "json",
) -> None:
    """Основна функція аналізу лог-файлів."""
    log_path = Path(log_file)
    output_path = Path(output)

    if not log_path.exists():
        logging.error(f"Файл логу не знайдено: {log_path}")
        return

    logging.info(f"Loading access log from {log_path}...")

    entries: list[LogEntry] = []
    error_ips: Counter[str] = Counter()
    status_breakdown: dict[str, Counter[int]] = defaultdict(Counter)
    detected_attacks: list[dict[str, Any]] = []

    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            entry = parse_log_line(line)
            if not entry:
                continue
            entries.append(entry)

            # Підрахунок помилок (статус-коди >= min_status)
            if entry.status >= min_status:
                error_ips[entry.ip] += 1
                status_breakdown[entry.ip][entry.status] += 1

            # Перевірка на атаки
            for attack_name, pattern in ATTACK_PATTERNS.items():
                if pattern.search(entry.uri):
                    logging.warning(
                        f'Potential {attack_name} attack from {entry.ip}: "{entry.method} {entry.uri}"'
                    )
                    detected_attacks.append(
                        {
                            "attack_type": attack_name,
                            "ip": entry.ip,
                            "method": entry.method,
                            "uri": entry.uri,
                            "time": entry.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                        }
                    )

    if entries:
        min_time = min(e.timestamp for e in entries)
        max_time = max(e.timestamp for e in entries)
        logging.info(
            f"Processed {len(entries)} log entries from {min_time} to {max_time}."
        )

    # Демонстрація підсумку в консоль
    print(f"\n=== Top-{top_n} IP Addresses with Error Statuses (>= {min_status}) ===")
    top_list = error_ips.most_common(top_n)
    for ip, count in top_list:
        breakdown_str = ", ".join(
            f"{st}: {cnt}" for st, cnt in sorted(status_breakdown[ip].items())
        )
        print(f"{ip:<15} - {count} errors ({breakdown_str})")

    # Збереження результатів у файл
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if out_format.lower() == "csv":
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Category", "IP", "Count/Details", "Additional"])
            for ip, count in top_list:
                writer.writerow(["TopErrorIP", ip, count, dict(status_breakdown[ip])])
            for attack in detected_attacks:
                writer.writerow(
                    ["Attack", attack["ip"], attack["attack_type"], attack["uri"]]
                )
    else:  # json
        report = {
            "total_entries": len(entries),
            "top_error_ips": [
                {"ip": ip, "count": count, "breakdown": dict(status_breakdown[ip])}
                for ip, count in top_list
            ],
            "detected_attacks": detected_attacks,
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=4, ensure_ascii=False)

    logging.info(f"Analysis report saved to {output_path}")


def setup_parser(subparsers: argparse._SubParsersAction) -> None:
    """Підключення CLI аргументів для команди analyze."""
    parser = subparsers.add_parser(
        "analyze", help="Аналіз access.log веб-сервера (Завдання 2)"
    )
    parser.add_argument(
        "--log-file",
        type=str,
        default="labs/lab02/data/access.log",
        help="Шлях до вхідного log-файлу",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="labs/lab02/data/web_analysis_report.json",
        help="Шлях для збереження звіту",
    )
    parser.add_argument(
        "--min-status",
        type=int,
        default=400,
        help="Мінімальний статус-код помилки (за замовчуванням 400)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=5,
        help="Кількість топ IP у виводі (за замовчуванням 5)",
    )
    parser.add_argument(
        "--format",
        choices=["json", "csv"],
        default="json",
        help="Формат звіту (json/csv)",
    )