import pandas as pd
from datetime import datetime

def export_to_csv(classes, filename=None):

    if filename is None:
        timestamp = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
        filename = f'export/export_{timestamp}.csv'
    
    try:
        classes.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\n\033[42mЭКСПОРТ УСПЕШЕН:\033[0m\n")
        print(f"Данные экспортированы: {filename}")
        print(f"Количество записей: {len(classes)}")
        return filename
    except Exception as e:
        print(f"\n\033[41mОШИБКА ПРИ ЭКСПОРТЕ:\033[0m\n")
        print(f"Не удалось экспортировать данные: {e}")
        return None

