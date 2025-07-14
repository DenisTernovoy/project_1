import datetime as dt
import logging
import pathlib
from typing import Optional

import pandas as pd
from dateutil.relativedelta import relativedelta

from src.utils import write_reports


base_path = pathlib.Path(__file__).resolve().parent.parent
directory = base_path / "logs/reports.log"

logger = logging.getLogger("reports")
file_handler = logging.FileHandler(directory, encoding="utf-8", mode="w")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


@write_reports()
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> str:
    """Функция возвращает траты по заданной категории за последние три месяца (от переданной даты)"""

    logger.debug("Начало работы функции spending_by_category")

    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    transactions = transactions[transactions["Категория"] == category]

    if date:
        try:
            date_to = dt.datetime.fromisoformat(date).date()
            logger.info(f"Удалось осуществить преобразование даты, введенной пользователем")
        except ValueError:
            logger.error(f"Не удалось осуществить преобразование даты, введенной пользователем")
            date_to = dt.datetime.now().date()
    else:
        logger.info(f"Дата не введена пользователем. Установлена текущая дата")
        date_to = dt.datetime.now().date()

    date_from = date_to - relativedelta(months=3)

    start_date = pd.Timestamp(date_from)
    end_date = pd.Timestamp(date_to)

    transactions = transactions[
        (transactions["Дата операции"] >= start_date) & (transactions["Дата операции"] <= end_date)
    ]

    result = transactions[["Дата операции", "Категория", "Сумма операции с округлением"]]
    dict_format = result.to_json(orient="records", force_ascii=False, date_format="iso", indent=4)

    logger.info("Функция spending_by_category отработала корректно")
    return dict_format
