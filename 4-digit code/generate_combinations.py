# generate_combinations.py
# Объединенный скрипт для генерации комбинаций 4-значного кода

import json
import os

# Определяем путь к скрипту для правильного поиска конфига и папки вывода
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILENAME = "config_4.json"
CONFIG_FILE_PATH = os.path.join(SCRIPT_DIR, CONFIG_FILENAME)
OUTPUT_FOLDER = SCRIPT_DIR  # Теперь папка вывода - та же, где и скрипт
CODES_SUBFOLDER = "codes"


# --- Общие функции сохранения и загрузки ---

def save_combinations_to_json(combinations, filename):
    """Сохраняет список комбинаций в JSON-файл, удаляя старый файл, если он существует."""
    full_folder_path = os.path.join(OUTPUT_FOLDER, CODES_SUBFOLDER)
    os.makedirs(full_folder_path, exist_ok=True)
    filepath = os.path.join(full_folder_path, filename)

    # Удаляем старый файл, если он существует
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            # print(f"[Инфо] Старый файл {filepath} удален.") # Опционально, для отладки
        except OSError as e:
            print(f"[Предупреждение] Не удалось удалить старый файл {filepath}: {e}")
            # Продолжаем выполнение, так как запись может перезаписать файл

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(combinations, f, indent=2)
        return filepath, None
    except Exception as e:
        return None, e


def load_config():
    """Загружает конфигурацию из config_4.json, находящегося рядом со скриптом."""
    try:
        with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
        config['start_code'] = [int(d) for d in config['start_code']]
        return config
    except Exception as e:
        print(f"[Ошибка] Загрузка конфига {CONFIG_FILE_PATH}: {e}")
        return None


# --- Логика генерации из generate_forward.py ---

def generate_forward_combinations():
    """Генерирует 4-значные комбинации от 0000 до 9990 с шагом 10."""
    combinations = []
    for i in range(0, 10000, 10):
        code_str = f"{i:04d}"
        code_list = [int(digit) for digit in code_str]
        combinations.append(code_list)
    return combinations


def run_generate_forward():
    """Основная функция генерации 'С начала'."""
    filename = "combinations_forward.json"
    print(f"[Генерация] Создание списка комбинаций (0000 -> 9990)...")
    combinations = generate_forward_combinations()
    total_count = len(combinations)
    print(f"[Генерация] Всего комбинаций: {total_count}")
    filepath, error = save_combinations_to_json(combinations, filename)
    if error:
        print(f"[Ошибка] Сохранение: {error}")
    else:
        print(f"[Готово] Файл сохранен: {filepath}")
        print("[Готово] Генерация завершена.")


# --- Логика генерации из generate_reverse.py ---

def generate_reverse_combinations():
    """Генерирует 4-значные комбинации от 9990 до 0000 с шагом 10."""
    combinations = []
    for i in range(9990, -1, -10):
        code_str = f"{i:04d}"
        code_list = [int(digit) for digit in code_str]
        combinations.append(code_list)
    return combinations


def run_generate_reverse():
    """Основная функция генерации 'С конца'."""
    filename = "combinations_reverse.json"
    print(f"[Генерация] Создание списка комбинаций (9990 -> 0000)...")
    combinations = generate_reverse_combinations()
    total_count = len(combinations)
    print(f"[Генерация] Всего комбинаций: {total_count}")
    filepath, error = save_combinations_to_json(combinations, filename)
    if error:
        print(f"[Ошибка] Сохранение: {error}")
    else:
        print(f"[Готово] Файл сохранен: {filepath}")
        print("[Готово] Генерация завершена.")


# --- Логика генерации из generate_continue_forward.py ---

def generate_continue_forward_combinations(start_code):
    """Генерирует комбинации от текущего кода до 9990."""
    combinations = []
    # Предполагаем, что префикс состоит из первых 3 цифр, а последняя всегда 0 для проверки
    base_prefix_value = start_code[0] * 100 + start_code[1] * 10 + start_code[2]
    # Считаем до 999 (так как последняя цифра всегда 0)
    end_value = 999
    if base_prefix_value > end_value:
        print(f"[Предупреждение] Начальный код {base_prefix_value:03d} больше конечного {end_value}.")
        return combinations

    count = (end_value - base_prefix_value) + 1
    for i in range(count):
        current_value = base_prefix_value + i
        digit0 = current_value // 100
        digit1 = (current_value // 10) % 10
        digit2 = current_value % 10
        # Формируем комбинацию с 0 в последнем слоте, как это делает брутфорс
        combination = [digit0, digit1, digit2, 0]
        combinations.append(combination)
    return combinations


def run_generate_continue_forward(start_code):
    """Основная функция генерации 'Продолжить' -> 'Прибавить'."""
    filename = "combinations_continue_forward.json"
    print(f"[Генерация] Создание списка комбинаций продолжения с {''.join(map(str, start_code))} (прибавить)...")
    combinations = generate_continue_forward_combinations(start_code)
    total_count = len(combinations)
    print(f"[Генерация] Всего комбинаций: {total_count}")
    filepath, error = save_combinations_to_json(combinations, filename)
    if error:
        print(f"[Ошибка] Сохранение: {error}")
    else:
        print(f"[Готово] Файл сохранен: {filepath}")
        print("[Готово] Генерация завершена.")


# --- Логика генерации из generate_continue_reverse.py ---

def generate_continue_reverse_combinations(start_code):
    """Генерирует комбинации от текущего кода до 0000."""
    combinations = []
    # Предполагаем, что префикс состоит из первых 3 цифр, а последняя всегда 0 для проверки
    base_prefix_value = start_code[0] * 100 + start_code[1] * 10 + start_code[2]
    # Считаем до 000 (так как последняя цифра всегда 0)
    start_value = base_prefix_value
    end_value = 0
    if start_value < end_value:
        print(f"[Предупреждение] Начальный код {start_value:03d} меньше конечного {end_value}.")
        return combinations

    count = (start_value - end_value) + 1
    for i in range(count):
        current_value = start_value - i
        digit0 = current_value // 100
        digit1 = (current_value // 10) % 10
        digit2 = current_value % 10
        # Формируем комбинацию с 0 в последнем слоте, как это делает брутфорс
        combination = [digit0, digit1, digit2, 0]
        combinations.append(combination)
    return combinations


def run_generate_continue_reverse(start_code):
    """Основная функция генерации 'Продолжить' -> 'Отнять'."""
    filename = "combinations_continue_reverse.json"
    print(f"[Генерация] Создание списка комбинаций продолжения с {''.join(map(str, start_code))} (отнять)...")
    combinations = generate_continue_reverse_combinations(start_code)
    total_count = len(combinations)
    print(f"[Генерация] Всего комбинаций: {total_count}")
    filepath, error = save_combinations_to_json(combinations, filename)
    if error:
        print(f"[Ошибка] Сохранение: {error}")
    else:
        print(f"[Готово] Файл сохранен: {filepath}")
        print("[Готово] Генерация завершена.")


# --- Основная точка входа ---

def main():
    """Определяет тип генерации на основе конфигурации и запускает соответствующую функцию."""
    print("[Генерация] Загрузка конфигурации...")
    config = load_config()
    if not config:
        print("[Ошибка] Конфигурация не загружена. Генерация остановлена.")
        return

    direction = config.get("direction", "С начала")
    print(f"[Генерация] Направление: {direction}")

    if direction == "С начала":
        run_generate_forward()
    elif direction == "С конца":
        run_generate_reverse()
    elif direction == "Продолжить":
        start_code = config["start_code"]
        continue_direction = config.get("continue_direction", "increase")
        if continue_direction == "increase":
            run_generate_continue_forward(start_code)
        elif continue_direction == "decrease":
            run_generate_continue_reverse(start_code)
        else:
            print(f"[Ошибка] Неверное значение continue_direction: {continue_direction}")
    else:
        print(f"[Ошибка] Неверное значение direction: {direction}")


if __name__ == '__main__':
    main()
