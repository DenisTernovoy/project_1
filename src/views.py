import datetime as dt
import json
import logging
import pathlib

from src.utils import (filter_cards_data, get_card_data, get_currency, get_data, get_stocks, get_top_transactions,
                       greetings)

base_path = pathlib.Path(__file__).resolve().parent.parent
directory = base_path / "logs/views.log"

logger = logging.getLogger("views")
file_handler = logging.FileHandler(directory, encoding="utf-8", mode="w")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


def main_views(timestamp: str = str(dt.datetime.now())) -> str:
    """Функция принимает на вход дату и возвращает статистику о банковских операциях пользователя"""

    logger.debug("Начало работы функции main_views")
    logger.debug("Попытка прочитать данные из Excel")
    main_data = get_data("../data/operations.xlsx")
    logger.debug("Данные из Excel успешно прочитаны")
    logger.debug("Попытка отфильтровать данные из Excel")
    filtered_data = filter_cards_data(main_data, str(timestamp))
    logger.debug("Данные из Excel успешно отфильтрованы")

    logger.debug("Переход к созданию словаря с данными")

    default_dict = {
        "greetings": greetings(),
        "cards": get_card_data(filtered_data),
        "top_transactions": get_top_transactions(filtered_data),
        "currency_rates": get_currency("../user_settings.json"),
        "stock_prices": get_stocks("../user_settings.json"),
    }

    logger.info("Словарь с данными успешно создан")

    result = json.dumps(default_dict, ensure_ascii=False, indent=4)
    logger.info("Словарь с данными переведен в JSON-строку")

    return result
