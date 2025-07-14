import datetime as dt
from typing import Optional

import pandas as pd
from dateutil.relativedelta import relativedelta


def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> str:
    """Функция возвращает траты по заданной категории за последние три месяца (от переданной даты)"""

    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    transactions = transactions[transactions["Категория"] == category]

    if date:
        try:
            date_to = dt.datetime.fromisoformat(date).date()
        except ValueError:
            date_to = dt.datetime.now().date()
    else:
        date_to = dt.datetime.now().date()

    date_from = date_to - relativedelta(months=3)

    start_date = pd.Timestamp(date_from)
    end_date = pd.Timestamp(date_to)

    transactions = transactions[
        (transactions["Дата операции"] >= start_date) & (transactions["Дата операции"] <= end_date)
    ]

    result = transactions[["Дата операции", "Категория", "Сумма операции с округлением"]]
    dict_format = result.to_json(orient="records", force_ascii=False, date_format="iso", indent=4)

    return dict_format
