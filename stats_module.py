import pandas as pd
from datetime import datetime, timedelta

def view_stat(classes, date):

    print("\n\033[42mСТАТИСТИКА:\033[0m\n")

    classes['Дата'] = pd.to_datetime(classes['Дата и время начала']).dt.date
    
    current_date = date.date() if isinstance(date, datetime) else date
    day_data = classes[classes['Дата'] == current_date]
    
    weekday = current_date.weekday()
    week_start = current_date - timedelta(days=weekday)
    week_end = week_start + timedelta(days=6)
    week_data = classes[(classes['Дата'] >= week_start) & (classes['Дата'] <= week_end)]
    
    avg_by_sport = classes.groupby('Вид спорта')['Число мест (занято)'].mean()
    print("Средняя посещаемость по каждому виду спорта:")
    print(avg_by_sport.to_string())
    
    print()
    min_sport = avg_by_sport.idxmin()
    max_sport = avg_by_sport.idxmax()
    print(f"Вид спорта с наименьшей посещаемостью: {min_sport} ({avg_by_sport[min_sport]:.2f})")
    print(f"Вид спорта с наибольшей посещаемостью: {max_sport} ({avg_by_sport[max_sport]:.2f})")
    
    print()
    print(f"Общее количество тренировок в неделю: {len(week_data)}")
    
    print()
    day_visitors = day_data['Число мест (занято)'].sum() if len(day_data) > 0 else 0
    week_visitors = week_data['Число мест (занято)'].sum() if len(week_data) > 0 else 0
    date_str = current_date.strftime('%Y-%m-%d')
    print(f"Общее число посетивших в день ({date_str}): {day_visitors}")
    print(f"Общее число посетивших в неделю ({week_start} - {week_end}): {week_visitors}")
    
    print()
    if len(day_data) > 0:
        day_occupancy = (day_data['Число мест (занято)'].sum() / day_data['Число мест (всего)'].sum()) * 100
        print(f"Процент заполняемости в день ({date_str}): {day_occupancy:.2f}%")
    
    if len(week_data) > 0:
        week_occupancy = (week_data['Число мест (занято)'].sum() / week_data['Число мест (всего)'].sum()) * 100
        print(f"Процент заполняемости в неделю ({week_start} - {week_end}): {week_occupancy:.2f}%")
    
    print()
    print("Процент заполняемости по виду спорта:")
    for sport in classes['Вид спорта'].unique():
        sport_data = classes[classes['Вид спорта'] == sport]
        if len(sport_data) > 0:
            sport_occupancy = (sport_data['Число мест (занято)'].sum() / sport_data['Число мест (всего)'].sum()) * 100
            print(f"{sport}: {sport_occupancy:.2f}%")
