import json
from typing import Any
from unittest.mock import MagicMock, mock_open, patch

import pytest

from src.utils import (filter_cards_data, get_card_data, get_currency, get_data, get_stocks, get_top_transactions,
                       greetings, write_reports)


@pytest.mark.parametrize(
    "hour, expected", [(3, "Доброй ночи"), (9, "Доброе утро"), (16, "Добрый день"), (23, "Добрый вечер")]
)
@patch("datetime.datetime")
def test_greetings(mock_now: Any, hour: int, expected: str) -> None:
    mock_data = MagicMock()
    mock_hour = MagicMock()
    mock_hour.hour = hour
    mock_data.time.return_value = mock_hour
    mock_now.now.return_value = mock_data
    assert greetings() == expected


@patch("pandas.read_excel")
def test_get_data(mock_read: Any) -> None:
    mock_dict = MagicMock()
    mock_dict.to_dict.return_value = {"A": 1, "Б": 2}

    mock_read.return_value = mock_dict

    assert get_data("") == {"A": 1, "Б": 2}


def test_filter_cards_data(transactions: list[dict]) -> None:
    result = [
        {
            "Дата операции": "03.01.2018 15:03:35",
            "Дата платежа": "04.01.2018",
            "Номер карты": "*7197",
            "Статус": "OK",
            "Сумма операции": -73.06,
            "Валюта операции": "RUB",
            "Сумма платежа": -73.06,
            "Валюта платежа": "RUB",
            "Кэшбэк": 0,
            "Категория": "Супермаркеты",
            "MCC": 5499.0,
            "Описание": "Magazin 25",
            "Бонусы (включая кэшбэк)": 1,
            "Округление на инвесткопилку": 0,
            "Сумма операции с округлением": 73.06,
        },
        {
            "Дата операции": "03.01.2018 14:55:21",
            "Дата платежа": "05.01.2018",
            "Номер карты": "*7197",
            "Статус": "OK",
            "Сумма операции": -21.0,
            "Валюта операции": "RUB",
            "Сумма платежа": -21.0,
            "Валюта платежа": "RUB",
            "Кэшбэк": 0,
            "Категория": "Красота",
            "MCC": 5977.0,
            "Описание": "OOO Balid",
            "Бонусы (включая кэшбэк)": 0,
            "Округление на инвесткопилку": 0,
            "Сумма операции с округлением": 21.0,
        },
        {
            "Дата операции": "01.01.2018 20:27:51",
            "Дата платежа": "04.01.2018",
            "Номер карты": "*7197",
            "Статус": "OK",
            "Сумма операции": -316.0,
            "Валюта операции": "RUB",
            "Сумма платежа": -316.0,
            "Валюта платежа": "RUB",
            "Кэшбэк": 0,
            "Категория": "Красота",
            "MCC": 5977.0,
            "Описание": "OOO Balid",
            "Бонусы (включая кэшбэк)": 6,
            "Округление на инвесткопилку": 0,
            "Сумма операции с округлением": 316.0,
        },
        {
            "Дата операции": "01.01.2018 12:49:53",
            "Дата платежа": "01.01.2018",
            "Номер карты": "*7197",
            "Статус": "OK",
            "Сумма операции": -3000.0,
            "Валюта операции": "RUB",
            "Сумма платежа": -3000.0,
            "Валюта платежа": "RUB",
            "Кэшбэк": 0,
            "Категория": "Переводы",
            "MCC": 0,
            "Описание": "Линзомат ТЦ Юность",
            "Бонусы (включая кэшбэк)": 0,
            "Округление на инвесткопилку": 0,
            "Сумма операции с округлением": 3000.0,
        },
    ]
    assert filter_cards_data(transactions, "2018-01-03 00:00:00") == result


def test_filter_cards_data_valid(transactions: list[dict]) -> None:
    with pytest.raises(ValueError) as e:
        filter_cards_data(transactions, "03.01.2018")
        assert str(e.value) == "Неверный формат даты"


def test_get_card_data(transactions: list[dict]) -> None:
    result = [
        {"last_digits": "4556", "total_spent": 250.0, "cashback": 2.5},
        {"last_digits": "5441", "total_spent": 157204.0, "cashback": 1572.04},
        {"last_digits": "7197", "total_spent": 7069.95, "cashback": 70.7},
    ]
    assert get_card_data(transactions) == result


def test_get_card_data_valid() -> None:
    assert get_card_data([]) == [{}]


def test_get_top_transactions(transactions: list[dict]) -> None:
    result = [
        {"date": "10.01.2018", "amount": -87068.0, "category": 0, "description": "Перевод с карты"},
        {"date": "10.01.2018", "amount": -40068.0, "category": 0, "description": "Перевод с карты"},
        {"date": "10.01.2018", "amount": -30068.0, "category": 0, "description": "Перевод с карты"},
        {"date": "01.01.2018", "amount": -3000.0, "category": "Переводы", "description": "Линзомат ТЦ Юность"},
        {"date": "04.01.2018", "amount": -1065.9, "category": "Супермаркеты", "description": "Пятёрочка"},
    ]
    assert get_top_transactions(transactions) == result


@patch("requests.get")
def test_get_currency(mock_get: Any) -> None:
    mock_status = MagicMock()
    mock_status.status_code = 200
    mock_get.return_value = mock_status
    mock_get.return_value.json.return_value = {"conversion_rate": 100}
    mock_data = {"user_currencies": ["USD"]}
    mock_json = json.dumps(mock_data)
    with patch("builtins.open", mock_open(read_data=mock_json)):
        assert get_currency("") == [{"currency": "USD", "rate": 100}]


@patch("requests.get")
def test_get_currency_valid(mock_get: Any) -> None:
    mock_status = MagicMock()
    mock_status.status_code = 100
    mock_get.return_value = mock_status
    mock_get.return_value.json.return_value = {"conversion_rate": 100}
    mock_data = {"user_currencies": ["USD"]}
    mock_json = json.dumps(mock_data)
    with patch("builtins.open", mock_open(read_data=mock_json)):
        assert get_currency("") == [{}]


@patch("requests.get")
def test_get_currency_valid_2(mock_get: Any) -> None:
    mock_status = MagicMock()
    mock_status.status_code = 200
    mock_get.return_value = mock_status
    mock_get.return_value.json.return_value = {"conversion_rate": 100}
    mock_data: dict = {"user_currencies": []}
    mock_json = json.dumps(mock_data)
    with patch("builtins.open", mock_open(read_data=mock_json)):
        assert get_currency("") == [{}]


@patch("requests.get")
def test_get_stocks(mock_get: Any) -> None:
    mock_status = MagicMock()
    mock_status.status_code = 200
    mock_get.return_value = mock_status
    mock_get.return_value.json.return_value = {"Time Series (5min)": {"2025-06-30 19:55:00": {"4. close": 1000}}}
    mock_data = {"user_stocks": ["AAPL"]}
    mock_json = json.dumps(mock_data)
    with patch("builtins.open", mock_open(read_data=mock_json)):
        assert get_stocks("") == [{"stock": "AAPL", "price": 1000}]


@patch("requests.get")
def test_get_stocks_valid(mock_get: Any) -> None:
    mock_status = MagicMock()
    mock_status.status_code = 100
    mock_get.return_value = mock_status
    mock_get.return_value.json.return_value = {"Time Series (5min)": {"2025-06-30 19:55:00": {"4. close": 1000}}}
    mock_data = {"user_stocks": ["AAPL"]}
    mock_json = json.dumps(mock_data)
    with patch("builtins.open", mock_open(read_data=mock_json)):
        assert get_stocks("") == [{}]


@patch("requests.get")
def test_get_stocks_valid_2(mock_get: Any) -> None:
    mock_status = MagicMock()
    mock_status.status_code = 200
    mock_get.return_value = mock_status
    mock_get.return_value.json.return_value = {"Time Series (5min)": {"2025-06-30 19:55:00": {"4. close": 1000}}}
    mock_data: dict = {"user_stocks": []}
    mock_json = json.dumps(mock_data)
    with patch("builtins.open", mock_open(read_data=mock_json)):
        assert get_stocks("") == [{}]


@patch("requests.get")
def test_get_stocks_valid_3(mock_get: Any) -> None:
    mock_status = MagicMock()
    mock_status.status_code = 200
    mock_get.return_value = mock_status
    mock_get.return_value.json.return_value = {"Time": {}}
    mock_data: dict = {"user_stocks": ["AAPL"]}
    mock_json = json.dumps(mock_data)
    with patch("builtins.open", mock_open(read_data=mock_json)):
        assert get_stocks("") == []


def test_write_reports() -> None:
    @write_reports()
    def func_test(a: int, b: int) -> str:
        summ = a + b
        return json.dumps(summ)

    result = func_test(1, 2)

    with open("func_test.json") as file:
        data = json.load(file)

    assert data == json.loads(result)


def test_write_reports_2() -> None:
    @write_reports("FileName")
    def func_test(a: int, b: int) -> str:
        summ = a + b
        return json.dumps(summ)

    result = func_test(1, 2)

    with open("FileName.json") as file:
        data = json.load(file)

    assert data == json.loads(result)
