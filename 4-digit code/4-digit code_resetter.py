# 3-digit_code_resetter.py
import ctypes
import time
import json
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE_PATH = os.path.join(script_dir, "config_3.json")

user32 = ctypes.WinDLL('user32', use_last_error=True)
SCANCODE_F = 0x21
SCANCODE_BACKSPACE = 0x0E
KEYEVENTF_KEYUP = 0x0002

# Предполагается, что механизм вращения такой же, как и для 4-значного
DIGIT_HOLD = {
    0: 6.20, 1: 1.35, 2: 2.00, 3: 2.50, 4: 3.00,
    5: 3.55, 6: 4.00, 7: 4.60, 8: 5.15, 9: 5.65,
}

SETTLE_TIME = 1.00
SLOT_SWITCH_DELAY = 0.5
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

def wait_for_backspace():
    print("[Ожидание] Нажмите Backspace в игре для старта...")
    while True:
        result = user32.GetAsyncKeyState(0x08)
        if result & 0x8000:
            print("[Старт] Сброс кода начат.")
            time.sleep(0.5)
            break
        time.sleep(0.1)

def reset_code():
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

    start_code = config["start_code"]
    current_code = config["current_code"].copy()
    current_slot = config["slot"]
    direction = config.get("direction", "С начала")

    print(f"[Конфиг] Направление: {direction}")
    print(f"[Конфиг] Целевой код: {''.join(map(str, start_code))}")

    wait_for_backspace()

    if current_code == start_code:
        print("[Инфо] Код уже установлен.")
        if current_slot == 0:
            print("[Готово] Система в начальном положении.")
        else:
            delta = (0 - current_slot + length) % length
            print(f"[Слот] Возврат на 0: {delta}x[F]")
            switch_slot(delta)
            print("[Готово] Система возвращена в начальное положение.")
    else:
        print(f"[Сброс] {''.join(map(str, current_code))} → {''.join(map(str, start_code))}")
        for i in range(length): # 0, 1, 2 для 3-значного
            if current_code[i] != start_code[i]:
                delta = (i - current_slot + length) % length
                if delta != 0:
                    print(f"[Слот] {current_slot} → {i}: {delta}x[F]")
                    switch_slot(delta)
                    time.sleep(SLOT_SWITCH_DELAY)
                    current_slot = i
                current_digit = current_code[i]
                target_digit = start_code[i]
                rotations = (target_digit - current_digit + 10) % 10
                if rotations != 0:
                    print(f"[Цифра] Слот {i}: {current_digit} → {target_digit} ({rotations} оборотов)")
                    set_digit(rotations)
                    current_code[i] = target_digit

        # Возврат в слот 0 после сброса
        final_slot = 0
        delta = (final_slot - current_slot + length) % length
        if delta != 0:
            print(f"[Слот] Возврат на 0: {delta}x[F]")
            switch_slot(delta)
            time.sleep(SLOT_SWITCH_DELAY)

        print("[Готово] Код сброшен и система в начальном положении.")

    print("[Завершено] Готов к следующему этапу.")

if __name__ == '__main__':
    reset_code()
