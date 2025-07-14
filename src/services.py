import calendar
import datetime as dt
import json
import logging
import pathlib
from collections import defaultdict
from typing import Any

from src.utils import filter_cards_data


base_path = pathlib.Path(__file__).resolve().parent.parent
directory = base_path / "logs/services.log"

logger = logging.getLogger("services")
file_handler = logging.FileHandler(directory, encoding="utf-8", mode="w")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


def category_cashback(data: list[dict], year: int, month: int) -> str:
    """Функция принимает на вход данные о банковских транзакциях, год и месяц,
    за которые проводится анализ и возвращает словарь с повышенными категориями кэшбэка"""

    logger.debug("Начало работы функции category_cashback")

    last_day = calendar.monthrange(year, month)[1]
    date = dt.datetime(year=year, month=month, day=last_day).isoformat()
    filtered_data = filter_cards_data(data, date)

    cashback_dict: Any = defaultdict(int)

    for i in filtered_data:
        cashback_dict[i["Категория"]] += i["Сумма операции с округлением"] // 100

    logger.info("Функция category_cashback отработала корректно")
    return json.dumps(dict(cashback_dict), indent=4, ensure_ascii=False)
