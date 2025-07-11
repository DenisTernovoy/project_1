import calendar
import datetime as dt
import json
from collections import defaultdict
from typing import Any

from src.utils import filter_cards_data


def category_cashback(data: list[dict], year: int, month: int) -> str:
    """Функция принимает на вход данные о банковских транзакциях, год и месяц,
    за которые проводится анализ и возвращает словарь с повышенными категориями кэшбэка"""

    last_day = calendar.monthrange(year, month)[1]
    date = dt.datetime(year=year, month=month, day=last_day).isoformat()
    filtered_data = filter_cards_data(data, date)

    cashback_dict: Any = defaultdict(int)

    for i in filtered_data:
        cashback_dict[i["Категория"]] += i["Сумма операции с округлением"] // 100

    return json.dumps(dict(cashback_dict), indent=4, ensure_ascii=False)
