import os
from datetime import datetime
import pandas as pd


def log_action(action_type, details, old_data=None, new_data=None):
    # Создаем папку logs, если её нет
    os.makedirs('logs', exist_ok=True)
    
    log_file = 'logs/classes_changes.log'
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"\n[{timestamp}] {action_type}: {details}\n")
        
        if old_data is not None:
            if isinstance(old_data, pd.Series):
                f.write("Старые данные:\n")
                for key, value in old_data.items():
                    f.write(f"  {key}: {value}\n")
            elif isinstance(old_data, dict):
                f.write("Старые данные:\n")
                for key, value in old_data.items():
                    f.write(f"  {key}: {value}\n")
        
        if new_data is not None:
            if isinstance(new_data, pd.Series):
                f.write("Новые данные:\n")
                for key, value in new_data.items():
                    f.write(f"  {key}: {value}\n")
            elif isinstance(new_data, dict):
                f.write("Новые данные:\n")
                for key, value in new_data.items():
                    f.write(f"  {key}: {value}\n")
        
        f.write("-" * 80 + "\n")


def log_add_class(new_class_data):
    details = f"Добавлено новое занятие: {new_class_data.get('Вид спорта', 'N/A')} | {new_class_data.get('Тренер', 'N/A')} | {new_class_data.get('Дата и время начала', 'N/A')}"
    log_action('ADD', details, new_data=new_class_data)


def log_delete_class(deleted_class_data):
    details = f"Удалено занятие: {deleted_class_data.get('Вид спорта', 'N/A')} | {deleted_class_data.get('Тренер', 'N/A')} | {deleted_class_data.get('Дата и время начала', 'N/A')}"
    log_action('DELETE', details, old_data=deleted_class_data)


def log_update_class(field_name, old_value, new_value, class_data):
    details = f"Изменено поле '{field_name}' занятия: {class_data.get('Вид спорта', 'N/A')} | {class_data.get('Тренер', 'N/A')} | {class_data.get('Дата и время начала', 'N/A')}"
    old_data = {field_name: old_value}
    new_data = {field_name: new_value}
    log_action('UPDATE', details, old_data=old_data, new_data=new_data)

