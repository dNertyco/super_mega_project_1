import os
from datetime import datetime, timedelta

import pandas as pd
import matplotlib.pyplot as plt

from data import *
from schedule_module import get_week_range


def export_week_schedule_to_png(classes, date, filename=None):
    week_start, week_end = get_week_range(date)

    df = classes.copy()
    df['Дата'] = pd.to_datetime(df['Дата и время начала']).dt.date
    df['Время'] = pd.to_datetime(df['Дата и время начала']).dt.strftime('%H:%M')

    week_df = df[(df['Дата'] >= week_start) & (df['Дата'] <= week_end)].copy()

    if len(week_df) == 0:
        print("За выбранную неделю занятий нет, экспорт в PNG не выполнен.")
        return None

    week_df = week_df.sort_values(['Дата', 'Время']).reset_index(drop=True)

    days_ru = {
        'Monday': 'Понедельник',
        'Tuesday': 'Вторник',
        'Wednesday': 'Среда',
        'Thursday': 'Четверг',
        'Friday': 'Пятница',
        'Saturday': 'Суббота',
        'Sunday': 'Воскресенье',
    }

    columns = [
        'День',
        'Время',
        'Вид спорта',
        'Тренер',
        'Длительность, мин',
        'Занято мест',
        'Всего мест',
    ]
    rows = []

    for offset in range(7):
        current_date = week_start + timedelta(days=offset)
        eng_day = current_date.strftime('%A')
        day_name = days_ru.get(eng_day, eng_day)

        day_slice = week_df[week_df['Дата'] == current_date]

        # Заголовок дня всегда, даже если занятий нет
        rows.append([day_name, '', '', '', '', '', ''])

        for _, row in day_slice.iterrows():
            rows.append(
                [
                    '',
                    row['Время'],
                    row['Вид спорта'],
                    row['Тренер'],
                    row['Продолжительность (мин)'],
                    row['Число мест (занято)'],
                    row['Число мест (всего)'],
                ]
            )

    table_df = pd.DataFrame(rows, columns=columns)

    os.makedirs('export', exist_ok=True)
    if filename is None:
        timestamp = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
        filename = f'export/week_schedule_{timestamp}.png'

    # Формат страницы A4 (в дюймах), горизонтальная ориентация ~ 11.69 x 8.27
    fig, ax = plt.subplots(figsize=(11.69, 8.27))
    ax.axis('off')

    table = ax.table(
        cellText=table_df.values,
        colLabels=table_df.columns,
        loc='center',
        cellLoc='center',
    )

    # Стилизация таблицы
    n_rows, n_cols = table_df.shape

    # Шапка
    for col in range(n_cols):
        cell = table[0, col]
        cell.set_facecolor('#3949ab')
        cell.get_text().set_color('white')
        cell.get_text().set_weight('bold')
        cell.set_edgecolor('white')
        cell.set_linewidth(1.0)

    # Строки с днями и занятиями
    day_row_flags = []
    for i, r in table_df.iterrows():
        is_day_row = bool(r['День']) and (not r['Время'])
        day_row_flags.append(is_day_row)

    lesson_row_index = 0
    for i in range(n_rows):
        table_row = i + 1  # т.к. 0 — шапка
        is_day_row = day_row_flags[i]

        if is_day_row:
            bg = '#eeeeee'
            weight = 'bold'
        else:
            lesson_row_index += 1
            bg = '#ffffff' if lesson_row_index % 2 else '#f7f7f7'
            weight = 'normal'

        for col in range(n_cols):
            cell = table[table_row, col]
            cell.set_facecolor(bg)
            cell.get_text().set_weight(weight)
            cell.set_edgecolor('#bdbdbd')
            cell.set_linewidth(0.5)

            # Делаем строки с занятиями выше
            if not is_day_row:
                cell.set_height(cell.get_height() * 1.5)

    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.2)

    title = f'Расписание на неделю {week_start} - {week_end}'
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)

    plt.tight_layout()
    fig.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close(fig)

    print(f'Экспорт расписания недели в PNG выполнен: {filename}')
    return filename