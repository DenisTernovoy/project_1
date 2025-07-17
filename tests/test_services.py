import json
from typing import Any
from unittest.mock import patch

from src.services import category_cashback


@patch("src.services.filter_cards_data")
def test_category_cashback(mock_data: Any) -> None:
    mock_data.return_value = [{"Категория": "Супермаркеты", "Сумма операции с округлением": 100}]
    result = json.dumps({"Супермаркеты": 1}, indent=4, ensure_ascii=False)

    assert category_cashback([{}], 1, 1) == result
