import pandas as pd
from datetime import datetime, timedelta

from data import *
from input import *
from log_module import *


def get_classes_for_date(target_date):
    """Получает все занятия на конкретную дату"""
    classes['Дата'] = pd.to_datetime(classes['Дата и время начала']).dt.date
    current_date = target_date.date() if isinstance(target_date, datetime) else target_date
    day_data = classes[classes['Дата'] == current_date].copy()
    # Сортируем по времени начала
    day_data['Время начала'] = pd.to_datetime(day_data['Дата и время начала'])
    day_data = day_data.sort_values('Время начала').reset_index(drop=True)
    # Убираем служебные колонки
    day_data = day_data.drop(columns=['Дата', 'Время начала'])
    return day_data


def change_active_class(day_classes):
    """Изменяет активное занятие по номеру"""
    global active_class_index
    
    print("\n\033[41mСМЕНА АКТИВНОГО ЗАНЯТИЯ:\033[0m\n")
    
    if len(day_classes) == 0:
        print("На выбранную дату нет занятий.")
        return
    
    display_df = day_classes.copy()
    display_df.index = range(1, len(display_df) + 1)
    
    print("Доступные занятия:")
    print(display_df)
    
    if active_class_index < len(day_classes):
        print(f"\nАктивное занятие: №{active_class_index + 1}")
    
    choice = universal_input(
        "\nВыберите номер занятия: ",
        input_type='int',
        valid_options=list(range(1, len(day_classes) + 1))
    )
    
    active_class_index = choice - 1


def get_active_class_index_in_global():
    """Получает индекс активного занятия в глобальном DataFrame classes"""
    global active_class_index
    day_classes = get_classes_for_date(date)
    if len(day_classes) == 0 or active_class_index >= len(day_classes):
        return None
    
    active_class = day_classes.iloc[active_class_index]
    # Находим индекс в глобальном classes по нескольким полям для точности
    mask = (classes['Дата и время начала'] == active_class['Дата и время начала']) & \
           (classes['Тренер'] == active_class['Тренер']) & \
           (classes['Вид спорта'] == active_class['Вид спорта']) & \
           (classes['Продолжительность (мин)'] == active_class['Продолжительность (мин)'])
    matching_indices = classes[mask].index
    if len(matching_indices) > 0:
        return matching_indices[0]
    return None


def delete_active_class():
    """Удаляет активное занятие"""
    global active_class_index, classes
    
    day_classes = get_classes_for_date(date)
    if len(day_classes) == 0 or active_class_index >= len(day_classes):
        print("Нет активного занятия для удаления.")
        return
    
    active_class = day_classes.iloc[active_class_index]
    print("\n\033[41mУДАЛЕНИЕ ЗАНЯТИЯ:\033[0m\n")
    print("Активное занятие:")
    display_df = pd.DataFrame([active_class])
    display_df.index = [1]
    print(display_df.to_string())
    
    confirm = universal_input(
        "\nВы уверены, что хотите удалить это занятие? (да/нет): ",
        input_type='text',
        valid_options=['да', 'нет']
    )
    
    if confirm == 'да':
        global_idx = get_active_class_index_in_global()
        if global_idx is not None:
            deleted_class = classes.iloc[global_idx].copy()
            classes = classes.drop(index=global_idx).reset_index(drop=True)
            log_delete_class(deleted_class)
            print("Занятие успешно удалено.")
            # Сбрасываем активное занятие на первое
            active_class_index = 0
        else:
            print("Ошибка: не удалось найти занятие для удаления.")
    else:
        print("Удаление отменено.")


def change_class_time():
    """Изменяет время начала активного занятия"""
    global classes, active_class_index
    
    day_classes = get_classes_for_date(date)
    if len(day_classes) == 0 or active_class_index >= len(day_classes):
        print("Нет активного занятия для изменения.")
        return
    
    global_idx = get_active_class_index_in_global()
    if global_idx is None:
        print("Ошибка: не удалось найти занятие для изменения.")
        return
    
    active_class = classes.iloc[global_idx]
    print("\n\033[41mИЗМЕНЕНИЕ ВРЕМЕНИ ЗАНЯТИЯ:\033[0m\n")
    print("Текущее занятие:")
    display_df = pd.DataFrame([active_class])
    display_df.index = [1]
    print(display_df.to_string())
    
    current_start = datetime.strptime(active_class['Дата и время начала'], '%Y-%m-%d %H:%M')
    print(f"\nТекущее время начала: {current_start.strftime('%H:%M')}")
    
    new_time_str = input("Введите новое время начала в формате HH:MM: ")
    try:
        new_time = datetime.strptime(new_time_str, '%H:%M').time()
        new_datetime = datetime.combine(current_start.date(), new_time)
        new_datetime_str = new_datetime.strftime('%Y-%m-%d %H:%M')
        
        # Создаем копию для проверки
        test_classes = classes.copy()
        test_classes.loc[global_idx, 'Дата и время начала'] = new_datetime_str
        
        # Получаем все занятия на эту дату из тестового набора для проверки
        test_classes['Дата'] = pd.to_datetime(test_classes['Дата и время начала']).dt.date
        current_date = date.date() if isinstance(date, datetime) else date
        test_day_classes = test_classes[test_classes['Дата'] == current_date].copy()
        test_day_classes['Время начала'] = pd.to_datetime(test_day_classes['Дата и время начала'])
        test_day_classes = test_day_classes.sort_values('Время начала').reset_index(drop=True)
        test_day_classes = test_day_classes.drop(columns=['Дата', 'Время начала'])
        
        # Проверяем через validate_schedule
        error = validate_schedule(test_day_classes)
        if error:
            print(f"Ошибка: {error}")
        else:
            old_value = active_class['Дата и время начала']
            classes.loc[global_idx, 'Дата и время начала'] = new_datetime_str
            log_update_class('Дата и время начала', old_value, new_datetime_str, active_class)
            print("Время занятия успешно изменено.")
    except ValueError:
        print("Ошибка: неверный формат времени. Используйте HH:MM")


def change_class_duration():
    """Изменяет длительность активного занятия"""
    global classes, active_class_index
    
    day_classes = get_classes_for_date(date)
    if len(day_classes) == 0 or active_class_index >= len(day_classes):
        print("Нет активного занятия для изменения.")
        return
    
    global_idx = get_active_class_index_in_global()
    if global_idx is None:
        print("Ошибка: не удалось найти занятие для изменения.")
        return
    
    active_class = classes.iloc[global_idx]
    print("\n\033[41mИЗМЕНЕНИЕ ДЛИТЕЛЬНОСТИ ЗАНЯТИЯ:\033[0m\n")
    print("Текущее занятие:")
    display_df = pd.DataFrame([active_class])
    display_df.index = [1]
    print(display_df.to_string())
    
    current_duration = active_class['Продолжительность (мин)']
    print(f"\nТекущая длительность: {current_duration} минут")
    
    new_duration = universal_input(
        "Введите новую длительность в минутах: ",
        input_type='int',
        validation_func=lambda x: x > 0
    )
    
    # Создаем копию для проверки
    test_classes = classes.copy()
    test_classes.loc[global_idx, 'Продолжительность (мин)'] = new_duration
    
    # Получаем все занятия на эту дату из тестового набора для проверки
    test_classes['Дата'] = pd.to_datetime(test_classes['Дата и время начала']).dt.date
    current_date = date.date() if isinstance(date, datetime) else date
    test_day_classes = test_classes[test_classes['Дата'] == current_date].copy()
    test_day_classes['Время начала'] = pd.to_datetime(test_day_classes['Дата и время начала'])
    test_day_classes = test_day_classes.sort_values('Время начала').reset_index(drop=True)
    test_day_classes = test_day_classes.drop(columns=['Дата', 'Время начала'])
    
    # Проверяем через validate_schedule
    error = validate_schedule(test_day_classes)
    if error:
        print(f"Ошибка: {error}")
    else:
        old_value = active_class['Продолжительность (мин)']
        classes.loc[global_idx, 'Продолжительность (мин)'] = new_duration
        log_update_class('Продолжительность (мин)', old_value, new_duration, active_class)
        print("Длительность занятия успешно изменена.")


def change_class_trainer():
    """Изменяет тренера активного занятия"""
    global classes, active_class_index
    
    day_classes = get_classes_for_date(date)
    if len(day_classes) == 0 or active_class_index >= len(day_classes):
        print("Нет активного занятия для изменения.")
        return
    
    global_idx = get_active_class_index_in_global()
    if global_idx is None:
        print("Ошибка: не удалось найти занятие для изменения.")
        return
    
    active_class = classes.iloc[global_idx]
    print("\n\033[41mИЗМЕНЕНИЕ ТРЕНЕРА:\033[0m\n")
    print("Текущее занятие:")
    display_df = pd.DataFrame([active_class])
    display_df.index = [1]
    print(display_df.to_string())
    
    sport = active_class['Вид спорта']
    available_trainers = trainers.get(sport, [])
    
    if len(available_trainers) == 0:
        print(f"Нет доступных тренеров для вида спорта '{sport}'.")
        return
    
    print(f"\nДоступные тренеры для '{sport}':")
    trainers_df = pd.DataFrame({'Тренер': available_trainers})
    trainers_df.index = range(1, len(trainers_df) + 1)
    print(trainers_df)
    
    choice = universal_input(
        "\nВыберите номер тренера: ",
        input_type='int',
        valid_options=list(range(1, len(available_trainers) + 1))
    )
    
    new_trainer = available_trainers[choice - 1]
    
    # Создаем копию для проверки
    test_classes = classes.copy()
    test_classes.loc[global_idx, 'Тренер'] = new_trainer
    
    # Получаем все занятия на эту дату из тестового набора для проверки
    test_classes['Дата'] = pd.to_datetime(test_classes['Дата и время начала']).dt.date
    current_date = date.date() if isinstance(date, datetime) else date
    test_day_classes = test_classes[test_classes['Дата'] == current_date].copy()
    test_day_classes['Время начала'] = pd.to_datetime(test_day_classes['Дата и время начала'])
    test_day_classes = test_day_classes.sort_values('Время начала').reset_index(drop=True)
    test_day_classes = test_day_classes.drop(columns=['Дата', 'Время начала'])
    
    # Проверяем через validate_schedule (ограничение на время работы тренера уже проверяется там)
    error = validate_schedule(test_day_classes)
    if error:
        print(f"Ошибка: {error}")
    else:
        old_value = active_class['Тренер']
        classes.loc[global_idx, 'Тренер'] = new_trainer
        log_update_class('Тренер', old_value, new_trainer, active_class)
        print("Тренер успешно изменен.")


def update_registered_count():
    """Обновляет количество записавшихся на активное занятие"""
    global classes, active_class_index
    
    day_classes = get_classes_for_date(date)
    if len(day_classes) == 0 or active_class_index >= len(day_classes):
        print("Нет активного занятия для изменения.")
        return
    
    global_idx = get_active_class_index_in_global()
    if global_idx is None:
        print("Ошибка: не удалось найти занятие для изменения.")
        return
    
    active_class = classes.iloc[global_idx]
    print("\n\033[41mОБНОВЛЕНИЕ КОЛИЧЕСТВА ЗАПИСАВШИХСЯ:\033[0m\n")
    print("Текущее занятие:")
    display_df = pd.DataFrame([active_class])
    display_df.index = [1]
    print(display_df.to_string())
    
    max_places = int(active_class['Число мест (всего)'])
    
    new_value = universal_input(
        f"\nВведите новое количество записавшихся (0-{max_places}): ",
        input_type='int',
        valid_options=list(range(0, max_places + 1))
    )
    
    old_value = active_class['Число мест (занято)']
    classes.loc[global_idx, 'Число мест (занято)'] = new_value
    log_update_class('Число мест (занято)', old_value, new_value, active_class)
    print(f"Количество записавшихся успешно обновлено: {new_value}")


def add_class():
    """Добавляет новое занятие с проверкой на пересечение времени"""
    global classes, active_class_index
    
    print("\n\033[41mДОБАВЛЕНИЕ ЗАНЯТИЯ:\033[0m\n")
    
    # 1. Выбор вида спорта
    sports_list = list(sports)
    print("Доступные виды спорта:")
    sports_df = pd.DataFrame({'Вид спорта': sports_list})
    sports_df.index = range(1, len(sports_df) + 1)
    print(sports_df.to_string())
    
    sport_choice = universal_input(
        "\nВыберите номер вида спорта: ",
        input_type='int',
        valid_options=list(range(1, len(sports_list) + 1))
    )
    selected_sport = sports_list[sport_choice - 1]
    
    # 2. Выбор тренера
    available_trainers = trainers.get(selected_sport, [])
    if len(available_trainers) == 0:
        print(f"Нет доступных тренеров для вида спорта '{selected_sport}'.")
        return
    
    print(f"\nДоступные тренеры для '{selected_sport}':")
    trainers_df = pd.DataFrame({'Тренер': available_trainers})
    trainers_df.index = range(1, len(trainers_df) + 1)
    print(trainers_df.to_string())
    
    trainer_choice = universal_input(
        "\nВыберите номер тренера: ",
        input_type='int',
        valid_options=list(range(1, len(available_trainers) + 1))
    )
    selected_trainer = available_trainers[trainer_choice - 1]
    
    # 3. Ввод даты и времени начала
    date_str = input("\nВведите дату начала в формате YYYY-MM-DD: ")
    try:
        class_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        print("Ошибка: неверный формат даты. Используйте YYYY-MM-DD")
        return
    
    time_str = input("Введите время начала в формате HH:MM: ")
    try:
        class_time = datetime.strptime(time_str, '%H:%M').time()
        class_datetime = datetime.combine(class_date, class_time)
        class_datetime_str = class_datetime.strftime('%Y-%m-%d %H:%M')
    except ValueError:
        print("Ошибка: неверный формат времени. Используйте HH:MM")
        return
    
    # 4. Ввод продолжительности
    duration = universal_input(
        "Введите продолжительность в минутах: ",
        input_type='int',
        validation_func=lambda x: x > 0
    )
    
    # 5. Ввод числа мест всего
    total_places = universal_input(
        "Введите общее число мест: ",
        input_type='int',
        validation_func=lambda x: x > 0
    )
    
    # 6. Ввод числа мест занято
    occupied_places = universal_input(
        f"Введите число занятых мест (0-{total_places}): ",
        input_type='int',
        valid_options=list(range(0, total_places + 1))
    )
    
    # Создаем новое занятие
    new_class = {
        'Тренер': selected_trainer,
        'Вид спорта': selected_sport,
        'Дата и время начала': class_datetime_str,
        'Продолжительность (мин)': duration,
        'Число мест (всего)': total_places,
        'Число мест (занято)': occupied_places
    }
    
    # Получаем все занятия на эту дату для проверки
    classes['Дата'] = pd.to_datetime(classes['Дата и время начала']).dt.date
    day_data = classes[classes['Дата'] == class_date].copy()
    
    # Добавляем новое занятие в тестовый набор
    test_classes = day_data.copy()
    test_classes = pd.concat([test_classes, pd.DataFrame([new_class])], ignore_index=True)
    test_classes['Время начала'] = pd.to_datetime(test_classes['Дата и время начала'])
    test_classes = test_classes.sort_values('Время начала').reset_index(drop=True)
    test_classes = test_classes.drop(columns=['Дата', 'Время начала'], errors='ignore')
    
    # Проверяем через validate_schedule
    error = validate_schedule(test_classes)
    if error:
        print(f"\nОшибка: {error}")
        print("Занятие не добавлено.")
    else:
        # Добавляем занятие в глобальный DataFrame
        classes = pd.concat([classes, pd.DataFrame([new_class])], ignore_index=True)
        # Убираем служебную колонку Дата, если она была добавлена
        if 'Дата' in classes.columns:
            classes = classes.drop(columns=['Дата'])
        log_add_class(new_class)
        print("\nЗанятие успешно добавлено!")
        # Сбрасываем активное занятие
        active_class_index = 0


def view_schedule():
    """Просмотр расписания с подменю"""
    global active_class_index
    
    while True:
        print("\n\033[42mРАСПИСАНИЕ:\033[0m\n")
        
        day_classes = get_classes_for_date(date)
        
        # Проверяем, что активное занятие в пределах доступных
        if len(day_classes) > 0 and active_class_index >= len(day_classes):
            active_class_index = 0
        
        if len(day_classes) == 0:
            print(f"На дату {date.strftime('%Y-%m-%d')} нет занятий.")
        else:
            print(f"Занятия на {date.strftime('%Y-%m-%d')}:\n")
            display_df = day_classes.copy()
            display_df.index = range(1, len(display_df) + 1)
            print(display_df.to_string())
            
            # Выводим информационные списки
            active_class = day_classes.iloc[active_class_index] if active_class_index < len(day_classes) else None
            
            # 1. Окна для записи по дню
            print("\n\033[42mОКНА ДЛЯ ЗАПИСИ ПО ДНЮ:\033[0m\n")
            booking_day = get_booking_windows_by_day(active_class, date)
            if len(booking_day) > 0:
                print(booking_day.to_string())
            else:
                print("Нет доступных окон для записи на этот день.")
            
            # 2. Окна для записи по неделе
            print("\n\033[42mОКНА ДЛЯ ЗАПИСИ ПО НЕДЕЛЕ:\033[0m\n")
            booking_week = get_booking_windows_by_week(active_class, date)
            if len(booking_week) > 0:
                print(booking_week.to_string())
            else:
                print("Нет доступных окон для записи на эту неделю.")
            
            # 3. Занятия с 100% и 0% заполненностью
            print("\n\033[42mЗАНЯТИЯ С 100% ЗАПОЛНЕННОСТЬЮ (НЕДЕЛЯ):\033[0m\n")
            full_classes, empty_classes = get_full_and_empty_classes_by_week(date)
            if len(full_classes) > 0:
                print(full_classes.to_string())
            else:
                print("Нет полностью заполненных занятий.")
            
            print("\n\033[42mЗАНЯТИЯ С 0% ЗАПОЛНЕННОСТЬЮ (НЕДЕЛЯ):\033[0m\n")
            if len(empty_classes) > 0:
                print(empty_classes.to_string())
            else:
                print("Нет пустых занятий.")
            
            # 4. Отсортированный список по частоте встреч
            print("\n\033[42mЗАНЯТИЯ ПО ЧАСТОТЕ ВСТРЕЧ (НЕДЕЛЯ):\033[0m\n")
            frequency = get_classes_by_frequency_by_week(date)
            if len(frequency) > 0:
                print(frequency.to_string())
            else:
                print("Нет данных для отображения.")

            # Выводим номер активного занятия отдельной строкой внизу
            if active_class_index < len(day_classes):
                print(f"\nАктивное занятие: {active_class_index + 1}")
        
        print("\n\033[41mПОДМЕНЮ:\033[0m\n")
        print("1. Выбрать активное занятие")
        print("2. Удалить активное занятие")
        print("3. Изменить время занятия")
        print("4. Изменить длительность занятия")
        print("5. Изменить тренера")
        print("6. Обновить количество записавшихся")
        print("7. Добавить занятие")
        print("0. Возврат в главное меню")
        
        choice = universal_input(
            "\nВыберите действие: ",
            input_type='int',
            valid_options=[0, 1, 2, 3, 4, 5, 6, 7]
        )
        
        if choice == 0:
            break
        elif choice == 1:
            change_active_class(day_classes)
        elif choice == 2:
            delete_active_class()
        elif choice == 3:
            change_class_time()
        elif choice == 4:
            change_class_duration()
        elif choice == 5:
            change_class_trainer()
        elif choice == 6:
            update_registered_count()
        elif choice == 7:
            add_class()


def validate_schedule(schedule_df):
    """
    Проверяет расписание на корректность.
    
    Проверяет:
    1. Занятия должны быть строго в интервале 08:00–22:00
    2. Один тренер не может быть задействован одновременно на 2 занятиях
    3. Никакие занятия не должны пересекаться по времени
    
    Args:
        schedule_df: DataFrame с расписанием (должен содержать колонки:
                    'Тренер', 'Дата и время начала', 'Продолжительность (мин)')
    
    Returns:
        None если все проверки пройдены, иначе строка с причиной отклонения
    """
    if schedule_df.empty:
        return None
    
    # Проверка 1: Занятия должны быть в интервале 08:00–22:00
    for idx, row in schedule_df.iterrows():
        start_time_str = row['Дата и время начала']
        start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M')
        duration = int(row['Продолжительность (мин)'])
        end_time = start_time + timedelta(minutes=duration)
        
        # Проверяем время начала (должно быть >= 08:00)
        if start_time.hour < 8 or (start_time.hour == 8 and start_time.minute < 0):
            return f"Занятие начинается раньше 08:00: {start_time_str}"
        
        # Проверяем время окончания (должно быть <= 22:00)
        if end_time.hour > 22 or (end_time.hour == 22 and end_time.minute > 0):
            return f"Занятие заканчивается позже 22:00: {start_time_str} (окончание: {end_time.strftime('%H:%M')})"
    
    # Проверка 2 и 3: Пересечения по времени и один тренер на двух занятиях одновременно
    for i in range(len(schedule_df)):
        row1 = schedule_df.iloc[i]
        start1_str = row1['Дата и время начала']
        start1 = datetime.strptime(start1_str, '%Y-%m-%d %H:%M')
        duration1 = int(row1['Продолжительность (мин)'])
        end1 = start1 + timedelta(minutes=duration1)
        trainer1 = row1['Тренер']
        
        for j in range(i + 1, len(schedule_df)):
            row2 = schedule_df.iloc[j]
            start2_str = row2['Дата и время начала']
            start2 = datetime.strptime(start2_str, '%Y-%m-%d %H:%M')
            duration2 = int(row2['Продолжительность (мин)'])
            end2 = start2 + timedelta(minutes=duration2)
            trainer2 = row2['Тренер']
            
            # Проверяем пересечение по времени
            # Занятия пересекаются, если одно начинается до окончания другого и наоборот
            if not (end1 <= start2 or end2 <= start1):
                # Занятия пересекаются
                # Проверка 3: Никакие занятия не должны пересекаться
                return (f"Занятия пересекаются по времени: "
                       f"{start1_str} ({trainer1}) и {start2_str} ({trainer2})")
            
            # Проверка 2: Один тренер не может быть на двух занятиях одновременно
            if trainer1 == trainer2:
                # Если это один тренер, проверяем что занятия не пересекаются
                if not (end1 <= start2 or end2 <= start1):
                    return (f"Тренер {trainer1} задействован одновременно на двух занятиях: "
                           f"{start1_str} и {start2_str}")
    
    return None  # Все проверки пройдены


def get_week_range(target_date):
    """Получает начало и конец недели для заданной даты"""
    current_date = target_date.date() if isinstance(target_date, datetime) else target_date
    weekday = current_date.weekday()
    week_start = current_date - timedelta(days=weekday)
    week_end = week_start + timedelta(days=6)
    return week_start, week_end


def get_booking_windows_by_day(active_class, target_date):
    """Окна для записи по активному занятию - по дню"""
    if active_class is None or len(active_class) == 0:
        return pd.DataFrame()
    
    classes['Дата'] = pd.to_datetime(classes['Дата и время начала']).dt.date
    current_date = target_date.date() if isinstance(target_date, datetime) else target_date
    day_data = classes[classes['Дата'] == current_date].copy()
    
    # Ищем занятия того же вида спорта, где есть свободные места
    sport = active_class['Вид спорта']
    available = day_data[
        (day_data['Вид спорта'] == sport) & 
        (day_data['Число мест (занято)'] < day_data['Число мест (всего)'])
    ].copy()
    
    if len(available) > 0:
        available['Время начала'] = pd.to_datetime(available['Дата и время начала'])
        available = available.sort_values('Время начала').reset_index(drop=True)
        available = available.drop(columns=['Дата', 'Время начала'])
        available.index = range(1, len(available) + 1)
    
    return available


def get_booking_windows_by_week(active_class, target_date):
    """Окна для записи по активному занятию - в течение недели"""
    if active_class is None or len(active_class) == 0:
        return pd.DataFrame()
    
    week_start, week_end = get_week_range(target_date)
    classes['Дата'] = pd.to_datetime(classes['Дата и время начала']).dt.date
    week_data = classes[(classes['Дата'] >= week_start) & (classes['Дата'] <= week_end)].copy()
    
    # Ищем занятия того же вида спорта, где есть свободные места
    sport = active_class['Вид спорта']
    available = week_data[
        (week_data['Вид спорта'] == sport) & 
        (week_data['Число мест (занято)'] < week_data['Число мест (всего)'])
    ].copy()
    
    if len(available) > 0:
        available['Время начала'] = pd.to_datetime(available['Дата и время начала'])
        available = available.sort_values('Время начала').reset_index(drop=True)
        available = available.drop(columns=['Дата', 'Время начала'])
        available.index = range(1, len(available) + 1)
    
    return available


def get_full_and_empty_classes_by_week(target_date):
    """Занятия с 100% и 0% заполненностью - по неделе"""
    week_start, week_end = get_week_range(target_date)
    classes['Дата'] = pd.to_datetime(classes['Дата и время начала']).dt.date
    week_data = classes[(classes['Дата'] >= week_start) & (classes['Дата'] <= week_end)].copy()
    
    if len(week_data) == 0:
        return pd.DataFrame(), pd.DataFrame()
    
    # Вычисляем процент заполненности
    week_data['Заполненность %'] = (week_data['Число мест (занято)'] / week_data['Число мест (всего)'] * 100).round(2)
    
    # 100% заполненные
    full_classes = week_data[week_data['Заполненность %'] == 100.0].copy()
    
    # 0% заполненные
    empty_classes = week_data[week_data['Заполненность %'] == 0.0].copy()
    
    if len(full_classes) > 0:
        full_classes['Время начала'] = pd.to_datetime(full_classes['Дата и время начала'])
        full_classes = full_classes.sort_values('Время начала').reset_index(drop=True)
        full_classes = full_classes.drop(columns=['Дата', 'Время начала'])
        full_classes.index = range(1, len(full_classes) + 1)
    
    if len(empty_classes) > 0:
        empty_classes['Время начала'] = pd.to_datetime(empty_classes['Дата и время начала'])
        empty_classes = empty_classes.sort_values('Время начала').reset_index(drop=True)
        empty_classes = empty_classes.drop(columns=['Дата', 'Время начала'])
        empty_classes.index = range(1, len(empty_classes) + 1)
    
    return full_classes, empty_classes


def get_classes_by_frequency_by_week(target_date):
    """Отсортированный список занятий по частоте встреч в расписании - за неделю"""
    week_start, week_end = get_week_range(target_date)
    classes['Дата'] = pd.to_datetime(classes['Дата и время начала']).dt.date
    week_data = classes[(classes['Дата'] >= week_start) & (classes['Дата'] <= week_end)].copy()
    
    if len(week_data) == 0:
        return pd.DataFrame()
    
    # Группируем по виду спорта и тренеру, считаем частоту
    frequency = week_data.groupby(['Вид спорта', 'Тренер']).size().reset_index(name='Частота')
    frequency = frequency.sort_values('Частота', ascending=False).reset_index(drop=True)
    frequency.index = range(1, len(frequency) + 1)
    
    return frequency

