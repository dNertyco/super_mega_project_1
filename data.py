# БД

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

classes = pd.DataFrame(columns=[
    'Тренер', 
    'Вид спорта', 
    'Дата и время начала', 
    'Продолжительность (мин)', 
    'Число мест (всего)', 
    'Число мест (занято)'
])
date = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
active_class_index = 0  # Индекс активного занятия (по умолчанию первое)
export = None

# Данные для заполнения БД

sports = ['Плавание', 'Гимнастика', 'Бокс', 'Танцы']

trainers = {
    'Плавание': ['Иванов А.В.', 'Петрова М.С.', 'Сидоров Д.И.', 'Самойлова А.Л.'],
    'Гимнастика': ['Козлова Е.А.', 'Морозов В.П.', 'Волкова А.Н.', 'Куляхтина А.М.'],
    'Бокс': ['Соколов И.М.', 'Лебедев С.К.', 'Новиков П.Р.', 'Спиридонова А.Е.'],
    'Танцы': ['Федорова О.Л.', 'Михайлов А.Д.', 'Смирнова Т.В.', 'Орлова К.С.'],
}

# Заполняем БД
data = []
base_date = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
num_records = 15

for i in range(num_records):
    # Генерируем дату
    days_offset = int(np.random.randint(0, 14))
    hour = int(np.random.randint(8, 20))
    minute = int(np.random.choice([0, 15, 30, 45])) # Доступные минуты
    start_datetime = base_date + timedelta(days=days_offset, hours=hour-8, minutes=minute)
    
    total_places = np.random.randint(10, 31)
    sport = sports[i % len(sports)]
    trainer_index = (i // len(sports)) % len(trainers[sport])
    
    data.append({
        'Тренер': trainers[sport][trainer_index],
        'Вид спорта': sport,
        'Дата и время начала': start_datetime.strftime('%Y-%m-%d %H:%M'),
        'Продолжительность (мин)': np.random.choice([60, 90, 120]),
        'Число мест (всего)': total_places,
        'Число мест (занято)': np.random.randint(0, total_places + 1)
    })

classes = pd.DataFrame(data)