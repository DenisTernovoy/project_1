import json
from typing import Any
from unittest.mock import patch

from src.views import main_views


@patch("src.views.get_stocks")
@patch("src.views.get_currency")
@patch("src.views.get_top_transactions")
@patch("src.views.get_card_data")
@patch("src.views.greetings")
@patch("src.views.filter_cards_data")
@patch("src.views.get_data")
def test_main_views(
    mock_data: Any,
    mock_filter: Any,
    mock_greetings: Any,
    mock_get_card: Any,
    mock_get_top: Any,
    mock_get_currency: Any,
    mock_get_stocks: Any,
) -> None:

    mock_data.return_value = [{}]
    mock_filter.return_value = [{}]

    mock_greetings.return_value = 1
    mock_get_card.return_value = 1
    mock_get_top.return_value = 1
    mock_get_currency.return_value = 1
    mock_get_stocks.return_value = 1

    default_dict: dict = {"greetings": 1, "cards": 1, "top_transactions": 1, "currency_rates": 1, "stock_prices": 1}
    result = json.dumps(default_dict, indent=4)

    assert main_views("") == result
