import datetime as dt
import json
import os

import pandas as pd
import requests
from dotenv import load_dotenv


def greetings() -> str:
    """Функция возвращает приветствие в зависимости от текущего времени"""

    hour_now = dt.datetime.now().time().hour
    if 0 <= hour_now < 6:
        return "Доброй ночи"
    elif 6 <= hour_now < 12:
        return "Доброе утро"
    elif 12 <= hour_now < 18:
        return "Добрый день"
    else:
        return "Добрый вечер"


def get_data(file_path: str) -> list[dict]:
    """Функция принимает на вход путь до файла Excel
    и возвращает список словарей с данными о банковских операциях"""

    df = pd.read_excel(file_path)
    # df = df[df["Номер карты"].notnull()]
    new_df = df.to_dict("records")
    return new_df


def filter_cards_data(data_cards: list[dict], date: str) -> list[dict]:
    """Функция принимает на вход список словарей с данными о банковских
    операциях и возвращает отфильтрованные по дате данные по каждой карте"""

    filtered_list = []
    try:
        date_to = dt.datetime.fromisoformat(date)
    except ValueError:
        raise ValueError("Неверный формат даты")

    date_from = date_to.replace(day=1)

    for i in data_cards:
        date_transaction = dt.datetime.strptime(i["Дата операции"], "%d.%m.%Y %H:%M:%S")
        if date_from.date() <= date_transaction.date() <= date_to.date():
            filtered_list.append(i)

    return filtered_list


def get_card_data(data: list[dict]) -> list[dict]:
    """Функция принимает на вход список словарей с данными о банковских
    операциях и возвращает данные по каждой карте"""

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

    return card_data_list


def get_top_transactions(data: list[dict]) -> list[dict]:
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

    return top_sorted_list


def get_currency(file_path: str) -> list[dict]:
    """Функция принимает путь до JSON-файла с настройками пользователя
    и возвращает словарь с курсами валют"""

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
                result = response.json()
                currency_list.append({"currency": i, "rate": result["conversion_rate"]})
            else:
                return [{}]

        return currency_list

    return [{}]


def get_stocks(file_path: str) -> list[dict]:
    """Функция принимает путь до JSON-файла с настройками пользователя
    и возвращает словарь с курсами акций"""

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
                time_series = result["Time Series (5min)"]
                latest_timestamp = next(iter(time_series))
                stock_price_usd = float(time_series[latest_timestamp]["4. close"])
                currency_list.append({"stock": i, "price": stock_price_usd})
            else:
                return [{}]

        return currency_list

    return [{}]
