import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILENAME = "config_3.json"
CONFIG_FILE_PATH = os.path.join(SCRIPT_DIR, CONFIG_FILENAME)
OUTPUT_FOLDER = SCRIPT_DIR
CODES_SUBFOLDER = "codes"


# --- Общие функции сохранения и загрузки ---

def save_combinations_to_json(combinations, filename):
    """Сохраняет список комбинаций в JSON-файл, удаляя старый файл, если он существует."""
    full_folder_path = os.path.join(OUTPUT_FOLDER, CODES_SUBFOLDER)
    os.makedirs(full_folder_path, exist_ok=True)
    filepath = os.path.join(full_folder_path, filename)

    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except OSError as e:
            print(f"[Предупреждение] Не удалось удалить старый файл {filepath}: {e}")

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(combinations, f, indent=2)
        return filepath, None
    except Exception as e:
        return None, e


def load_config():
    """Загружает конфигурацию из config_3.json, находящегося рядом со скриптом."""
    try:
        with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
        config['start_code'] = [int(d) for d in config['start_code']]
        return config
    except Exception as e:
        print(f"[Ошибка] Загрузка конфига {CONFIG_FILE_PATH}: {e}")
        return None


# --- Логика генерации для 3-значных кодов ---

def generate_forward_combinations():
    """Генерирует 3-значные комбинации от 000 до 990 с шагом 10."""
    combinations = []
    for i in range(0, 1000, 10):
        code_str = f"{i:03d}"
        code_list = [int(digit) for digit in code_str]
        combinations.append(code_list)
    return combinations


def run_generate_forward():
    """Основная функция генерации 'С начала'."""
    filename = "combinations_forward.json"
    print(f"[Генерация] Создание списка комбинаций (000 -> 990)...")
    combinations = generate_forward_combinations()
    total_count = len(combinations)
    print(f"[Генерация] Всего комбинаций: {total_count}")
    filepath, error = save_combinations_to_json(combinations, filename)
    if error:
        print(f"[Ошибка] Сохранение: {error}")
    else:
        print(f"[Готово] Файл сохранен: {filepath}")
        print("[Готово] Генерация завершена.")


def generate_reverse_combinations():
    """Генерирует 3-значные комбинации от 990 до 000 с шагом 10."""
    combinations = []
    for i in range(990, -1, -10):  # 990 до 000
        code_str = f"{i:03d}"
        code_list = [int(digit) for digit in code_str]
        combinations.append(code_list)
    return combinations


def run_generate_reverse():
    """Основная функция генерации 'С конца'."""
    filename = "combinations_reverse.json"
    print(f"[Генерация] Создание списка комбинаций (990 -> 000)...")
    combinations = generate_reverse_combinations()
    total_count = len(combinations)
    print(f"[Генерация] Всего комбинаций: {total_count}")
    filepath, error = save_combinations_to_json(combinations, filename)
    if error:
        print(f"[Ошибка] Сохранение: {error}")
    else:
        print(f"[Готово] Файл сохранен: {filepath}")
        print("[Готово] Генерация завершена.")


def generate_continue_forward_combinations(start_code):
    """Генерирует комбинации от текущего 3-значного кода до 990."""
    combinations = []
    base_prefix_value = start_code[0] * 10 + start_code[1]
    end_value = 99
    if base_prefix_value > end_value:
        print(f"[Предупреждение] Начальный код {base_prefix_value:02d} больше конечного {end_value}.")
        return combinations

    count = (end_value - base_prefix_value) + 1
    for i in range(count):
        current_value = base_prefix_value + i
        digit0 = current_value // 10
        digit1 = current_value % 10
        combination = [digit0, digit1, 0]
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


def generate_continue_reverse_combinations(start_code):
    """Генерирует комбинации от текущего 3-значного кода до 000."""
    combinations = []
    base_prefix_value = start_code[0] * 10 + start_code[1]
    start_value = base_prefix_value
    end_value = 0
    if start_value < end_value:
        print(f"[Предупреждение] Начальный код {start_value:02d} меньше конечного {end_value}.")
        return combinations

    count = (start_value - end_value) + 1
    for i in range(count):
        current_value = start_value - i
        digit0 = current_value // 10
        digit1 = current_value % 10
        combination = [digit0, digit1, 0]
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
