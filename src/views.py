import datetime as dt
import json

from src.utils import (
    filter_cards_data,
    get_card_data,
    get_currency,
    get_data,
    get_stocks,
    get_top_transactions,
    greetings,
)


def main_views(timestamp: str = str(dt.datetime.now())) -> str:
    main_data = get_data("../data/operations.xlsx")
    filtered_data = filter_cards_data(main_data, str(timestamp))

    default_dict = {
        "greetings": greetings(),
        "cards": get_card_data(filtered_data),
        "top_transactions": get_top_transactions(filtered_data),
        "currency_rates": get_currency("../user_settings.json"),
        "stock_prices": get_stocks("../user_settings.json"),
    }

    result = json.dumps(default_dict, ensure_ascii=False, indent=4)

    return result
