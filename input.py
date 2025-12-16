from datetime import datetime

def universal_input(prompt, input_type='text', valid_options=None, validation_func=None):
    while True:
        user_input = input(prompt)
        
        # Валидация по типу
        if input_type == 'date':
            try:
                parsed_date = datetime.strptime(user_input, '%Y-%m-%d')
                if valid_options and parsed_date.date() not in valid_options:
                    print(f"Ошибка: Дата должна быть одной из доступных дат. Попробуйте снова.")
                    continue
                else:
                    return parsed_date.date()

            except Exception as e:
                print(f"Ошибка. Неверный формат даты. Используйте YYYY-MM-DD")
                continue
        
        elif input_type == 'int':
            try:
                value = int(user_input)
                if valid_options and value not in valid_options:
                    print(f"Ошибка: Значение должно быть одним из: {valid_options}. Попробуйте снова.")
                    continue
                if validation_func and not validation_func(value):
                    continue
                return value
            except ValueError:
                print("Ошибка: Введите целое число. Попробуйте снова.")
                continue
        
        elif input_type == 'text':
            if valid_options and user_input not in valid_options:
                print(f"Ошибка: Значение должно быть одним из: {valid_options}. Попробуйте снова.")
                continue
            if validation_func and not validation_func(user_input):
                continue
            return user_input
