import pandas as pd

from src.reports import spending_by_category


def test_spending_by_category(transactions: list[dict]) -> None:
    result = [
        {"Дата операции": "2018-01-08T14:21:23.000", "Категория": "Связь", "Сумма операции с округлением": 250.0}
    ]
    result_df = pd.DataFrame(result).to_json(orient="records", force_ascii=False, date_format="iso", indent=4)
    assert spending_by_category(pd.DataFrame(transactions), "Связь", "2018-03-01") == result_df


def test_spending_by_category_valid(transactions: list[dict]) -> None:
    result: list[dict] = [{}]
    result_df = pd.DataFrame(result).to_json(orient="records", force_ascii=False, date_format="iso", indent=4)
    assert spending_by_category(pd.DataFrame(transactions), "Связь", "12.01.2025") == result_df


def test_spending_by_category_valid2(transactions: list[dict]) -> None:
    result: list[dict] = [{}]
    result_df = pd.DataFrame(result).to_json(orient="records", force_ascii=False, date_format="iso", indent=4)
    assert spending_by_category(pd.DataFrame(transactions), "Связь") == result_df
