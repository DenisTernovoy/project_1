import datetime as dt
import json
import logging
import os
import pathlib
from collections.abc import Callable
from typing import Any

import pandas as pd
import requests
from dotenv import load_dotenv

base_path = pathlib.Path(__file__).resolve().parent.parent
directory = base_path / "logs/utils.log"

logger = logging.getLogger("utils")
file_handler = logging.FileHandler(directory, encoding="utf-8", mode="w")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


def greetings() -> str:
    """Функция возвращает приветствие в зависимости от текущего времени"""
    logger.debug("Начало работы функции greetings")

    hour_now = dt.datetime.now().time().hour
    if 0 <= hour_now < 6:
        logger.info("Функция greetings отработала корректно")
        return "Доброй ночи"
    elif 6 <= hour_now < 12:
        logger.info("Функция greetings отработала корректно")
        return "Доброе утро"
    elif 12 <= hour_now < 18:
        logger.info("Функция greetings отработала корректно")
        return "Добрый день"
    else:
        logger.info("Функция greetings отработала корректно")
        return "Добрый вечер"


def get_data(file_path: str) -> list[dict]:
    """Функция принимает на вход путь до файла Excel
    и возвращает список словарей с данными о банковских операциях"""

    logger.debug("Начало работы функции get_data")

    df = pd.read_excel(file_path)
    # df = df[df["Номер карты"].notnull()]
    new_df = df.to_dict("records")

    logger.info("Функция get_data отработала корректно")

    return new_df


def filter_cards_data(data_cards: list[dict], date: str) -> list[dict]:
    """Функция принимает на вход список словарей с данными о банковских
    операциях и возвращает отфильтрованные по дате данные по каждой карте"""

    logger.debug("Начало работы функции filter_cards_data")

    filtered_list = []
    try:
        date_to = dt.datetime.fromisoformat(date)
        logger.info("Попытка конвертации даты в функции filter_cards_data прошла успешно")
    except ValueError:
        logger.error("Попытка конвертации даты в функции filter_cards_data не удалась")
        raise ValueError("Неверный формат даты")

    date_from = date_to.replace(day=1)

    for i in data_cards:
        date_transaction = dt.datetime.strptime(i["Дата операции"], "%d.%m.%Y %H:%M:%S")
        if date_from.date() <= date_transaction.date() <= date_to.date():
            filtered_list.append(i)

    logger.info("Функция filter_cards_data отработала корректно")

    return filtered_list


def get_card_data(data: list[dict]) -> list[dict]:
    """Функция принимает на вход список словарей с данными о банковских
    операциях и возвращает данные по каждой карте"""

    logger.debug("Начало работы функции get_card_data")

    if data:
        df = pd.DataFrame(data)

        df_series = df.groupby("Номер карты")["Сумма операции с округлением"].sum()
        df_dict = df_series.to_dict()

        card_data_list = []
        for i in df_dict:
            card_data_dict = {
                "last_digits": i[-4:],
                "total_spent": round(df_dict[i], 2),
                "cashback": round(df_dict[i] / 100, 2),
            }
            card_data_list.append(card_data_dict)

        logger.info("Функция get_card_data отработала корректно")

        return card_data_list
    else:

        logger.info("Функция get_card_data не выявила данных по запросу")
        return [{}]


def get_top_transactions(data: list[dict]) -> list[dict]:
    """Функция принимает список транзакций и возвращает 5 наиболее дорогих транзакций"""

    logger.debug("Начало работы функции get_top_transactions")

    sorted_list = sorted(data, key=lambda x: x["Сумма операции с округлением"], reverse=True)

    top_sorted_list = []
    for i in sorted_list[:5]:
        transaction_dict = {
            "date": i["Дата операции"].split()[0],
            "amount": i["Сумма операции"],
            "category": i["Категория"],
            "description": i["Описание"],
        }
        top_sorted_list.append(transaction_dict)

    logger.info("Функция get_top_transactions отработала корректно")

    return top_sorted_list


def get_currency(file_path: str) -> list[dict]:
    """Функция принимает путь до JSON-файла с настройками пользователя
    и возвращает словарь с курсами валют"""

    logger.debug("Начало работы функции get_currency")

    load_dotenv()
    api = os.getenv("API_KEY_CURRENCY")

    with open(file_path, "r", encoding="utf-8") as file:
        data_json = json.load(file)

    if data_json["user_currencies"]:
        currency_list = []
        for i in data_json["user_currencies"]:
            url = f"https://v6.exchangerate-api.com/v6/{api}/pair/{i}/RUB"
            response = requests.get(url)
            status_code = response.status_code

            if status_code == 200:
                logger.info(f"Удалось осуществить запрос на сервер по API для {i}")
                result = response.json()
                currency_list.append({"currency": i, "rate": result["conversion_rate"]})
            else:
                logger.info("Не удалось осуществить запрос на сервер по API")
                return [{}]

        logger.info("Функция get_currency отработала корректно")
        return currency_list

    logger.info("Список валют, указанных пользователем пуст")
    return [{}]


def get_stocks(file_path: str) -> list[dict]:
    """Функция принимает путь до JSON-файла с настройками пользователя
    и возвращает словарь с курсами акций"""

    logger.debug("Начало работы функции get_stocks")

    load_dotenv()
    api = os.getenv("API_KEY_STOCK")

    with open(file_path, "r", encoding="utf-8") as file:
        data_json = json.load(file)

    if data_json["user_stocks"]:
        currency_list = []
        for i in data_json["user_stocks"]:
            param = "TIME_SERIES_INTRADAY"
            url = f"https://www.alphavantage.co/query?function={param}&symbol={i}&interval=5min&apikey={api}"
            response = requests.get(url)
            status_code = response.status_code

            if status_code == 200:
                result = response.json()
                if "Time Series (5min)" in result:
                    logger.info(f"Удалось осуществить запрос на сервер по API для {i}")
                    time_series = result["Time Series (5min)"]
                    latest_timestamp = next(iter(time_series))
                    stock_price_usd = float(time_series[latest_timestamp]["4. close"])
                    currency_list.append({"stock": i, "price": stock_price_usd})
                else:
                    logger.info(f"Не удалось осуществить запрос на сервер по API для {i}")
                    continue
            else:
                logger.info("Не удалось осуществить запрос на сервер по API")
                return [{}]

        logger.info("Функция get_stocks отработала корректно")
        return currency_list

    logger.info("Список акций, указанных пользователем пуст")
    return [{}]


def write_reports(file_name: str = "") -> Any:
    """Функция-декоратор с параметром, принимающая в качестве аргумента имя файла для записи результата
    работы функции"""

    logger.debug("Начало работы декоратора write_reports")

    def decorator(func: Callable) -> Callable:
        def wrapper(*args: list, **kwargs: dict) -> Any:
            if file_name == "":
                name: str = func.__name__
            else:
                name = file_name

            result = func(*args, **kwargs)

            with open(f"{name}.json", "w", encoding="utf-8") as file:
                file.write(result)

            logger.info("Декоратор отработал успешно")
            return result

        return wrapper

    return decorator
