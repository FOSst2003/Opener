import ctypes
import time
import json
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE_PATH = os.path.join(script_dir, "config_3.json")
COMBINATIONS_FOLDER = os.path.join(script_dir, "codes")

user32 = ctypes.WinDLL('user32', use_last_error=True)
SCANCODE_F = 0x21
KEYEVENTF_KEYUP = 0x0002

DIGIT_HOLD = {
    0: 6.20,
    1: 1.35,
    2: 2.00,
    3: 2.50,
    4: 3.00,
    5: 3.55,
    6: 4.00,
    7: 4.60,
    8: 5.15,
    9: 5.65,
}

SETTLE_TIME = 0.65
SLOT_SWITCH_DELAY = 0.1
KEY_PRESS_TIME = 0.05
KEY_RELEASE_TIME = 0.1


def press_key(sc):
    user32.keybd_event(0, sc, 0x0008, 0)


def release_key(sc):
    user32.keybd_event(0, sc, 0x0008 | KEYEVENTF_KEYUP, 0)


def switch_slot(count):
    if count == 0:
        return
    for _ in range(count):
        press_key(SCANCODE_F)
        time.sleep(KEY_PRESS_TIME)
        release_key(SCANCODE_F)
        time.sleep(KEY_RELEASE_TIME)


def set_digit(target):
    if target == 0:
        return
    hold_time = DIGIT_HOLD[target]
    press_key(SCANCODE_F)
    time.sleep(hold_time)
    release_key(SCANCODE_F)
    time.sleep(SETTLE_TIME)


def perform_full_circle():
    hold_time = DIGIT_HOLD[0]
    press_key(SCANCODE_F)
    time.sleep(hold_time)
    release_key(SCANCODE_F)
    time.sleep(SETTLE_TIME)


def load_config():
    try:
        with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
        config['start_code'] = [int(d) for d in config['start_code']]
        config['current_code'] = [int(d) for d in config['current_code']]
        return config
    except FileNotFoundError:
        print(f"[Ошибка] config_3.json не найден.")
        return None
    except Exception as e:
        print(f"[Ошибка] Загрузка конфига: {e}")
        return None


def load_combinations(direction, continue_direction=None):
    if direction == "С конца":
        filename = "combinations_reverse.json"
    elif direction == "Продолжить":
        if continue_direction == "decrease":
            filename = "combinations_continue_reverse.json"
        else:
            filename = "combinations_continue_forward.json"
    else:
        filename = "combinations_forward.json"

    filepath = os.path.join(COMBINATIONS_FOLDER, filename)

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            combinations = json.load(f)
        print(f"[Инфо] Загружен файл: {filename}")
        return combinations
    except FileNotFoundError:
        print(f"[Ошибка] Файл комбинаций не найден: {filepath}")
        return None
    except Exception as e:
        print(f"[Ошибка] Загрузка комбинаций: {e}")
        return None


def wait_for_backspace():
    print("[Ожидание] Нажмите Backspace в игре для старта перебора...")
    while True:
        result = user32.GetAsyncKeyState(0x08)
        if result & 0x8000:
            print("[Старт] Перебор начат.")
            time.sleep(0.5)
            break
        time.sleep(0.1)


def set_code_sequential(target_code, current_code_state):
    length = len(target_code)  # 3
    temp_current_code = current_code_state.copy()

    for i in range(length - 1):
        target_digit = target_code[i]
        current_digit = temp_current_code[i]
        if target_digit != current_digit:
            rotations = (target_digit - current_digit + 10) % 10
            if rotations != 0:
                set_digit(rotations)
                temp_current_code[i] = target_digit
        if i < length - 2:
            switch_slot(1)
            time.sleep(SLOT_SWITCH_DELAY)

    switch_slot(1)
    time.sleep(SLOT_SWITCH_DELAY)

    perform_full_circle()
    temp_current_code[2] = 0

    switch_slot(1)
    time.sleep(SLOT_SWITCH_DELAY)

    return temp_current_code


def format_time(seconds):
    if seconds < 0:
        return "0с"
    if seconds < 60:
        return f"{int(seconds)}с"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}м {secs}с"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours}ч {minutes}м {secs}с"


def brute_force_execute():
    print("[Инициализация] Загрузка конфигурации...")
    config = load_config()
    if not config:
        print("[Ошибка] Конфигурация не загружена.")
        input("Нажмите Enter для выхода...")
        return

    length = config["length"]
    if length != 3:
        print("[Ошибка] Поддерживаются только 3-значные коды.")
        input("Нажмите Enter для выхода...")
        return

    direction = config.get("direction", "С начала")
    continue_direction = config.get("continue_direction", "increase")
    print(f"[Конфиг] Направление: {direction}")
    if direction == "Продолжить":
        print(f"[Конфиг] Направление продолжения: {continue_direction}")

    print("[Инициализация] Загрузка комбинаций...")
    combinations = load_combinations(direction, continue_direction)
    if combinations is None:
        print("[Ошибка] Комбинации не загружены.")
        input("Нажмите Enter для выхода...")
        return

    total_combinations = len(combinations)
    print(f"[Готово] Загружено {total_combinations} комбинаций.")
    print("[Важно] Переключитесь в игру!")
    wait_for_backspace()

    print("[Инфо] Начинаем перебор с текущего состояния игры.")
    current_code_state = combinations[0].copy() if combinations else [0, 0, 0]
    current_code_state[2] = 0  # После полного круга третья цифра — 0
    print(f"[Старт] Предполагаемый код в игре: {''.join(map(str, current_code_state))}")

    start_time = time.time()
    last_iteration_times = []
    MAX_LAST_TIMES = 100
    ESTIMATED_TIME_PER_COMBINATION = 6.0

    for i, target_combination in enumerate(combinations):
        target_code_str = "".join(map(str, target_combination))

        iteration_start_time = time.time()

        current_code_state = set_code_sequential(target_combination, current_code_state)

        actual_iteration_time = time.time() - iteration_start_time

        if i > 0:
            last_iteration_times.append(actual_iteration_time)
            if len(last_iteration_times) > MAX_LAST_TIMES:
                last_iteration_times.pop(0)

            remaining_combinations = total_combinations - (i + 1)

            if len(last_iteration_times) >= 5:
                avg_time_per_combination = sum(last_iteration_times) / len(last_iteration_times)
                eta_seconds = avg_time_per_combination * remaining_combinations
                eta_str = format_time(eta_seconds)
            else:
                eta_seconds = ESTIMATED_TIME_PER_COMBINATION * remaining_combinations
                eta_str = format_time(eta_seconds)
        else:
            remaining_combinations = total_combinations - 1
            eta_seconds = ESTIMATED_TIME_PER_COMBINATION * remaining_combinations
            eta_str = format_time(eta_seconds)

        progress_percent = (i + 1) / total_combinations * 100
        print(f"[{i + 1}/{total_combinations}] ({progress_percent:.1f}%) Код: {target_code_str} | ETA: {eta_str}")

        if i < total_combinations - 1:
            time.sleep(SETTLE_TIME)

    total_time = time.time() - start_time
    print(f"\n[Готово] Перебор завершен за {format_time(total_time)}.")
    print(f"[Инфо] Проверено {total_combinations} комбинаций.")
    input("Нажмите Enter для выхода...")


if __name__ == '__main__':
    brute_force_execute()
