# Расписание спортшколы

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from data import *
from input import *
from stats_module import *
from export_module import *
from schedule_module import *
from visualization_module import *


def get_available_dates():
    dates = []
    for dt_str in classes['Дата и время начала']:
        try:
            dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M')
            dates.append(dt.date())
        except:
            continue
    return sorted(set(dates))

def change_date():
    global date, active_class_index

    print("\n\033[41mСМЕНА ДАТЫ:\033[0m\n")
    
    available_dates = get_available_dates()
    
    print("Доступные даты в базе данных:")
    for i, d in enumerate(available_dates):
        print(d.strftime('%Y-%m-%d'))
        
    date = universal_input(
        "\nВведите дату в формате YYYY-MM-DD: ",
        input_type='date',
        valid_options=available_dates
    )
    
    # Сбрасываем активное занятие на первое при смене даты
    active_class_index = 0

menu = [
    "Смотреть расписание",
    "Смотреть статистику",
    "Смотреть визуализацию",
    "Сменить дату отображения информации",
    "Экспорт в CSV",
]

while True:
    print("\n\n\033[41mГЛАВНОЕ МЕНЮ:\033[0m\n")
    for i, item in enumerate(menu):
        print(f"{i+1}. {item}")
    print("\nИнформация отображается на дату:", date.strftime('%Y-%m-%d'))
    
    choice_num = universal_input(
        "\nВыберите действие: ",
        input_type='int',
        valid_options=list(range(1, len(menu) + 1))
    )
    
    selected_item = menu[choice_num - 1]
    

    match selected_item:
        case "Сменить дату отображения информации":
            change_date()
        case "Смотреть расписание":
            view_schedule()
        case "Смотреть статистику":
            view_stat(classes, date)
        case "Смотреть визуализацию":
            create_visualizations()
        case "Экспорт в CSV":
            export_to_csv(classes)