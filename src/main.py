import pandas as pd

from src.reports import spending_by_category
from src.services import category_cashback
from src.utils import get_data
from src.views import main_views


def main_module():
    data = get_data("../data/operations.xlsx")

    year = int(input("Введите год для получения отчета: "))
    month = int(input("Введите месяц для получения отчета: "))

    date = input("Введите дату для получения данных с начала месяца, "
                 "на который выпадает входящая дата, по входящую дату: ")

    category = input("Введите категорию расходов для фильтрации: ")

    print(main_views(date))
    print(category_cashback(data, year, month))
    print(spending_by_category(pd.DataFrame(data), category, date))
