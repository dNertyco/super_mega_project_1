import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta

from data import *


def create_visualizations():
    """Создает все визуализации и сохраняет их в папку visualizations"""
    
    # Создаем папку visualizations, если её нет
    os.makedirs('visualizations', exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    
    print("\n\033[42mСОЗДАНИЕ ВИЗУАЛИЗАЦИЙ:\033[0m\n")
    
    # 1. Столбчатая диаграмма средней посещаемости по видам спорта
    filename1 = create_attendance_by_sport_chart(timestamp)
    if filename1:
        print(f"График 1 сохранен: {filename1}")
    
    # 2. Линейный график динамики посещаемости по дням недели
    filename2 = create_attendance_by_weekday_chart(timestamp)
    if filename2:
        print(f"График 2 сохранен: {filename2}")
    
    # 3. График частоты работы тренеров
    filename3 = create_trainer_frequency_chart(timestamp)
    if filename3:
        print(f"График 3 сохранен: {filename3}")
    
    print("\n\033[42mВИЗУАЛИЗАЦИИ СОЗДАНЫ УСПЕШНО!\033[0m\n")


def create_attendance_by_sport_chart(timestamp):
    """Строит столбчатую диаграмму средней посещаемости по видам спорта"""
    try:
        # Вычисляем среднюю посещаемость по видам спорта
        avg_by_sport = classes.groupby('Вид спорта')['Число мест (занято)'].mean()
        
        # Создаем график
        plt.figure(figsize=(10, 6))
        avg_by_sport.plot(kind='bar', color='steelblue', edgecolor='black')
        plt.title('Средняя посещаемость по видам спорта', fontsize=14, fontweight='bold')
        plt.xlabel('Вид спорта', fontsize=12)
        plt.ylabel('Средняя посещаемость', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        
        filename = f'visualizations/attendance_by_sport_{timestamp}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filename
    except Exception as e:
        print(f"Ошибка при создании графика средней посещаемости: {e}")
        return None


def create_attendance_by_weekday_chart(timestamp):
    """Строит линейный график динамики посещаемости по дням недели"""
    try:
        # Добавляем колонку с датой и днем недели
        classes['Дата'] = pd.to_datetime(classes['Дата и время начала']).dt.date
        classes['День недели'] = pd.to_datetime(classes['Дата и время начала']).dt.day_name()
        
        # Названия дней недели на русском
        days_ru = {
            'Monday': 'Понедельник',
            'Tuesday': 'Вторник',
            'Wednesday': 'Среда',
            'Thursday': 'Четверг',
            'Friday': 'Пятница',
            'Saturday': 'Суббота',
            'Sunday': 'Воскресенье'
        }
        classes['День недели RU'] = classes['День недели'].map(days_ru)
        
        # Группируем по дню недели и суммируем посещаемость
        attendance_by_day = classes.groupby('День недели RU')['Число мест (занято)'].sum()
        
        # Сортируем по порядку дней недели
        day_order = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
        attendance_by_day = attendance_by_day.reindex([day for day in day_order if day in attendance_by_day.index])
        
        # Создаем график
        plt.figure(figsize=(12, 6))
        attendance_by_day.plot(kind='line', marker='o', linewidth=2, markersize=8, color='coral')
        plt.title('Динамика посещаемости по дням недели', fontsize=14, fontweight='bold')
        plt.xlabel('День недели', fontsize=12)
        plt.ylabel('Общая посещаемость', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        
        filename = f'visualizations/attendance_by_weekday_{timestamp}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filename
    except Exception as e:
        print(f"Ошибка при создании графика динамики посещаемости: {e}")
        return None


def create_trainer_frequency_chart(timestamp):
    """Строит график частоты работы тренеров"""
    try:
        # Получаем всех тренеров из словаря trainers
        all_trainers = []
        for sport_trainers in trainers.values():
            all_trainers.extend(sport_trainers)
        all_trainers = sorted(set(all_trainers))
        
        # Подсчитываем частоту работы каждого тренера (количество занятий)
        trainer_frequency = classes.groupby('Тренер').size()
        
        # Создаем Series со всеми тренерами, заполняя нулями тех, у кого нет занятий
        trainer_frequency_full = pd.Series(index=all_trainers, dtype=int)
        trainer_frequency_full = trainer_frequency_full.fillna(0)
        trainer_frequency_full = trainer_frequency_full.add(trainer_frequency, fill_value=0)
        
        # Сортируем по убыванию частоты
        trainer_frequency_full = trainer_frequency_full.sort_values(ascending=False)
        
        # Создаем график
        plt.figure(figsize=(12, 6))
        trainer_frequency_full.plot(kind='bar', color='teal', edgecolor='black')
        plt.title('Частота работы тренеров (количество занятий за всё время)', fontsize=14, fontweight='bold')
        plt.xlabel('Тренер', fontsize=12)
        plt.ylabel('Количество занятий', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        
        filename = f'visualizations/trainer_frequency_{timestamp}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filename
    except Exception as e:
        print(f"Ошибка при создании графика частоты работы тренеров: {e}")
        return None

