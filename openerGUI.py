import sys
import os
import json
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QMessageBox, QRadioButton,
    QButtonGroup, QProgressBar, QTextEdit
)
from PyQt5.QtCore import Qt, QProcess


class CodeConfigurator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Конфигуратор кода")
        self.setGeometry(100, 100, 500, 450)

        self.tabs = QTabWidget()
        self.length = 4
        self.config_filename = ""
        self.scripts_base_dir = ""
        self.process = None

        self.init_ui()

    def init_ui(self):
        self.tab1 = self.create_tab1()
        self.tab3 = self.create_tab3()
        self.tab4 = self.create_tab4()
        self.tab5 = self.create_tab5()

        self.tabs.addTab(self.tab1, "Выбор длины")
        self.tabs.addTab(QWidget(), "Ввод кода")
        self.tabs.addTab(self.tab3, "Стартовая позиция")
        self.tabs.addTab(self.tab4, "Завершение")
        self.tabs.addTab(self.tab5, "Запуск")

        for i in range(1, 5):
            self.tabs.setTabVisible(i, False)

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def create_tab1(self):
        tab = QWidget()
        layout = QVBoxLayout()
        title = QLabel("Выберите длину кода:")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        btn3 = QPushButton("3-значный код")
        btn4 = QPushButton("4-значный код")

        btn3.clicked.connect(lambda: self.switch_to_code_tab(3))
        btn4.clicked.connect(lambda: self.switch_to_code_tab(4))

        layout.addWidget(btn3)
        layout.addWidget(btn4)
        tab.setLayout(layout)
        return tab

    def switch_to_code_tab(self, length):
        self.length = length
        self.scripts_base_dir = f"{self.length}-digit code"

        self.tabs.removeTab(1)
        self.tab2 = self.create_tab2(length)
        self.tabs.insertTab(1, self.tab2, f"Ввод кода ({length})")
        self.tabs.setTabVisible(1, True)
        self.switch_tab(1)

    def create_tab2(self, length=4):
        tab = QWidget()
        layout = QVBoxLayout()
        title = QLabel(f"Введите {length}-значный код:")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.code_inputs = []
        self.slot_buttons = []
        self.slot_group = QButtonGroup(self)

        code_layout = QHBoxLayout()
        for i in range(length):
            digit_layout = QVBoxLayout()

            line_edit = QLineEdit()
            line_edit.setMaxLength(1)
            line_edit.setFixedWidth(40)
            self.code_inputs.append(line_edit)
            digit_layout.addWidget(line_edit, alignment=Qt.AlignHCenter)

            slot_btn = QRadioButton()
            self.slot_buttons.append(slot_btn)
            self.slot_group.addButton(slot_btn, i)
            digit_layout.addWidget(slot_btn, alignment=Qt.AlignHCenter)

            code_layout.addLayout(digit_layout)
        layout.addLayout(code_layout)

        nav_layout = QHBoxLayout()
        back_btn = QPushButton("Назад")
        next_btn = QPushButton("Далее")
        back_btn.clicked.connect(lambda: self.tabs.setCurrentIndex(0))
        next_btn.clicked.connect(self.validate_tab2)
        nav_layout.addWidget(back_btn)
        nav_layout.addWidget(next_btn)
        layout.addLayout(nav_layout)

        tab.setLayout(layout)
        return tab

    def create_tab3(self):
        tab = QWidget()
        layout = QVBoxLayout()
        title = QLabel("Выберите стартовую позицию:")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.position_group = QButtonGroup(self)

        self.start_radio = QRadioButton("С начала (все нули)")
        self.start_radio.setToolTip(
            f"Начать перебор с кода, состоящего из всех нулей (например, {'0' * self.length}).\n"
            "Это стандартная отправная точка и самый быстрый режим перебора."
        )
        self.position_group.addButton(self.start_radio, 0)
        layout.addWidget(self.start_radio)

        self.end_radio = QRadioButton("С конца (все девятки)")
        self.end_radio.setToolTip(
            f"Начать перебор с кода, состоящего из всех девяток (например, {'9' * self.length}).\n"
            "Из-за специфики механизма ввода, этот режим может занимать на ~55% больше времени,\n"
            "так как для установки цифры 9 требуется максимальное время удержания клавиши."
        )
        self.position_group.addButton(self.end_radio, 1)
        layout.addWidget(self.end_radio)

        custom_group = QVBoxLayout()
        self.custom_radio = QRadioButton("Продолжить код")
        self.custom_radio.setToolTip(
            "Продолжить перебор с определенного пользователем кода.\n"
            "Позволяет задать произвольный стартовый код и направление перебора (прибавить/отнять)."
        )
        self.position_group.addButton(self.custom_radio, 2)
        self.custom_radio.toggled.connect(self.toggle_custom_code)

        self.custom_code_input = QLineEdit()
        self.custom_code_input.setPlaceholderText("Введите текущий код")
        self.custom_code_input.setMaxLength(self.length)
        self.custom_code_input.setFixedWidth(100)
        self.custom_code_input.setEnabled(False)
        self.custom_code_input.setToolTip(
            f"Введите {self.length}-значный код, с которого следует продолжить перебор.\n"
            f"Например, если последний проверенный код был {'1' * (self.length - 1)}2, введите его здесь."
        )

        self.direction_group = QButtonGroup(self)
        self.increase_radio = QRadioButton("Прибавить")
        self.increase_radio.setToolTip(
            "Перебирать коды в порядке возрастания, начиная с введенного кода.\n"
            f"Например: {'1' * (self.length - 1)}0 -> {'1' * (self.length - 1)}1 -> ..."
        )
        self.decrease_radio = QRadioButton("Отнять")
        self.decrease_radio.setToolTip(
            "Из-за специфики механизма ввода, этот режим может занимать на ~55% больше времени.\n"
            "Перебирать коды в порядке убывания, начиная с введенного кода.\n"
            f"Например: {'1' * (self.length - 1)}0 -> {'0' * (self.length - 1)}9 -> ..."
        )
        self.increase_radio.setEnabled(False)
        self.decrease_radio.setEnabled(False)
        self.direction_group.addButton(self.increase_radio, 0)
        self.direction_group.addButton(self.decrease_radio, 1)

        increase_tooltip = QLabel("(?)")
        increase_tooltip.setToolTip(self.increase_radio.toolTip())
        decrease_tooltip = QLabel("(?)")
        decrease_tooltip.setToolTip(self.decrease_radio.toolTip())

        custom_group.addWidget(self.custom_radio)
        custom_group.addWidget(self.custom_code_input)

        increase_layout = QHBoxLayout()
        increase_layout.addWidget(self.increase_radio)
        increase_layout.addWidget(increase_tooltip)
        increase_layout.addStretch()
        custom_group.addLayout(increase_layout)

        decrease_layout = QHBoxLayout()
        decrease_layout.addWidget(self.decrease_radio)
        decrease_layout.addWidget(decrease_tooltip)
        decrease_layout.addStretch()
        custom_group.addLayout(decrease_layout)

        layout.addLayout(custom_group)

        nav_layout = QHBoxLayout()
        back_btn = QPushButton("Назад")
        next_btn = QPushButton("Далее")
        back_btn.clicked.connect(lambda: self.tabs.setCurrentIndex(1))
        next_btn.clicked.connect(self.validate_tab3)
        nav_layout.addWidget(back_btn)
        nav_layout.addWidget(next_btn)
        layout.addLayout(nav_layout)

        tab.setLayout(layout)
        return tab

    def create_tab4(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.final_label = QLabel(
            "Конфиг успешно сохранен!\nТеперь перейдите на вкладку 'Запуск' для выполнения скриптов.")
        self.final_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.final_label)

        go_to_run_btn = QPushButton("Перейти к запуску скриптов")
        go_to_run_btn.clicked.connect(lambda: self.switch_tab(4))
        layout.addWidget(go_to_run_btn, alignment=Qt.AlignCenter)

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn, alignment=Qt.AlignCenter)

        tab.setLayout(layout)
        return tab

    def create_tab5(self):
        tab = QWidget()
        layout = QVBoxLayout()
        title = QLabel("Запуск скриптов перебора")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        info_label = QLabel(
            "Скрипты будут запущены в следующем порядке:\n"
            "1. Генерация комбинаций\n"
            "2. Сброс кода\n"
            "3. Перебор комбинаций\n"
            "ВАЖНО: Для запуска скриптов 'Сброс' и 'Перебор'\n"
            "переключитесь в игру и нажмите Backspace!"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        self.generate_btn = QPushButton("1. Генерировать комбинации")
        self.reset_btn = QPushButton("2. Сбросить код")
        self.brute_force_btn = QPushButton("3. Начать перебор")

        self.generate_btn.clicked.connect(self.run_generate_script)
        self.reset_btn.clicked.connect(self.run_reset_script)
        self.brute_force_btn.clicked.connect(self.run_brute_force_script)

        self.reset_btn.setEnabled(False)
        self.brute_force_btn.setEnabled(False)

        layout.addWidget(self.generate_btn)
        layout.addWidget(self.reset_btn)
        layout.addWidget(self.brute_force_btn)

        self.progress_bar = QProgressBar()
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)

        layout.addWidget(QLabel("Прогресс:"))
        layout.addWidget(self.progress_bar)
        layout.addWidget(QLabel("Лог:"))
        layout.addWidget(self.log_output)

        nav_layout = QHBoxLayout()
        back_btn = QPushButton("Назад")
        back_btn.clicked.connect(lambda: self.switch_tab(3))
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.close)
        nav_layout.addWidget(back_btn)
        nav_layout.addWidget(close_btn)
        layout.addLayout(nav_layout)

        tab.setLayout(layout)
        return tab

    def toggle_custom_code(self, checked):
        self.custom_code_input.setEnabled(checked)
        self.increase_radio.setEnabled(checked)
        self.decrease_radio.setEnabled(checked)

    def switch_tab(self, index):
        if index < self.tabs.count():
            self.tabs.setTabVisible(index, True)
        self.tabs.setCurrentIndex(index)

    def validate_tab2(self):
        for i, input_field in enumerate(self.code_inputs):
            text = input_field.text()
            if not text.isdigit():
                QMessageBox.warning(self, "Ошибка", f"Введите цифру в позиции {i + 1}")
                return

        if not self.slot_group.checkedButton():
            QMessageBox.warning(self, "Ошибка", "Выберите слот для установки кода")
            return

        self.switch_tab(2)

    def validate_tab3(self):
        position_id = self.position_group.checkedId()
        if position_id == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите стартовую позицию")
            return

        if position_id == 2:
            code = self.custom_code_input.text()
            if not code.isdigit() or len(code) != self.length:
                QMessageBox.warning(self, "Ошибка", f"Введите {self.length}-значный код")
                return
            if self.direction_group.checkedId() == -1:
                QMessageBox.warning(self, "Ошибка", "Выберите направление продолжения")
                return

        self.save_configuration()
        self.switch_tab(3)

    def save_configuration(self):
        try:
            current_code = [int(input.text()) for input in self.code_inputs]
            selected_slot = self.slot_group.checkedId()

            position_id = self.position_group.checkedId()

            config = {
                "current_code": current_code,
                "length": self.length,
                "slot": selected_slot,
            }

            if position_id == 0:
                config["start_code"] = [0] * self.length
                config["direction"] = "С начала"
            elif position_id == 1:
                config["start_code"] = [9] * self.length
                config["direction"] = "С конца"
            elif position_id == 2:
                custom_code = [int(d) for d in self.custom_code_input.text()]
                config["start_code"] = custom_code
                config["direction"] = "Продолжить"
                config["continue_direction"] = (
                    "increase" if self.direction_group.checkedId() == 0 else "decrease"
                )

            folder = f"{self.length}-digit code"
            os.makedirs(folder, exist_ok=True)
            self.config_filename = os.path.join(folder, f"config_{self.length}.json")

            with open(self.config_filename, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения конфига: {str(e)}")

    def get_script_path(self, script_name):
        return os.path.join(self.scripts_base_dir, script_name)

    def run_generate_script(self):
        try:
            self.log_output.append("[Генерация] Запуск...")
            self.progress_bar.setValue(20)

            script_name = ""
            if self.length == 3:
                script_name = "generate_3digit_combinations.py"
            else:
                script_name = "generate_combinations.py"

            script_path = self.get_script_path(script_name)
            if not os.path.exists(script_path):
                raise FileNotFoundError(f"Скрипт '{script_name}' не найден в '{self.scripts_base_dir}'.")

            script_dir = self.scripts_base_dir
            result = subprocess.run(
                [sys.executable, script_name],
                capture_output=True,
                text=True,
                cwd=script_dir
            )

            if result.returncode == 0:
                self.log_output.append("[Генерация] Успешно завершена.")
                self.progress_bar.setValue(40)
                self.reset_btn.setEnabled(True)
                QMessageBox.information(self, "Успех", "Комбинации сгенерированы успешно!")
            else:
                error_msg = result.stderr if result.stderr else result.stdout
                self.log_output.append(f"[Ошибка] Генерация: {error_msg}")
                QMessageBox.critical(self, "Ошибка", f"Ошибка генерации:\n{error_msg}")

        except Exception as e:
            self.log_output.append(f"[Ошибка] Генерация: {str(e)}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка запуска генерации:\n{str(e)}")

    def run_reset_script(self):
        try:
            self.log_output.append("[Сброс] Запуск...")
            self.progress_bar.setValue(60)

            if self.length == 3:
                script_name = "3-digit_code_resetter.py"
            else:
                script_name = "4-digit code_resetter.py"

            script_path = self.get_script_path(script_name)
            if not os.path.exists(script_path):
                raise FileNotFoundError(f"Скрипт '{script_name}' не найден в '{self.scripts_base_dir}'.")

            self.process = QProcess(self)
            self.process.setWorkingDirectory(self.scripts_base_dir)
            self.process.setProcessChannelMode(QProcess.MergedChannels)
            self.process.readyReadStandardOutput.connect(self.handle_process_output)
            self.process.finished.connect(self.on_reset_finished)

            self.process.start(sys.executable, [script_name])

            self.log_output.append("[Сброс] Скрипт запущен. Переключитесь в игру и нажмите Backspace.")
            self.reset_btn.setEnabled(False)

        except Exception as e:
            self.log_output.append(f"[Ошибка] Сброс: {str(e)}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка запуска сброса:\n{str(e)}")

    def handle_process_output(self):
        if self.process:
            data = self.process.readAllStandardOutput()
            try:
                output = data.data().decode('utf-8')
            except UnicodeDecodeError:
                try:
                    output = data.data().decode('cp1251')
                except UnicodeDecodeError:
                    output = data.data().decode('utf-8', errors='ignore')
            self.log_output.append(output.strip())

    def on_reset_finished(self, exit_code, exit_status):
        self.process = None
        if exit_code == 0:
            self.log_output.append("[Сброс] Успешно завершен.")
            self.progress_bar.setValue(80)
            self.brute_force_btn.setEnabled(True)
            QMessageBox.information(self, "Успех", "Сброс кода завершен успешно!")
        else:
            self.log_output.append(f"[Ошибка] Сброс завершен с кодом {exit_code}.")
            QMessageBox.critical(self, "Ошибка", f"Сброс кода завершен с ошибкой (код {exit_code}).")

    def run_brute_force_script(self):
        try:
            self.log_output.append("[Перебор] Запуск...")
            self.progress_bar.setValue(90)

            if self.length == 3:
                script_name = "3-digit_brute_force_runner.py"
            else:
                script_name = "brute_force_runner.py"

            script_path = self.get_script_path(script_name)
            if not os.path.exists(script_path):
                raise FileNotFoundError(f"Скрипт '{script_name}' не найден в '{self.scripts_base_dir}'.")

            self.process = QProcess(self)
            self.process.setWorkingDirectory(self.scripts_base_dir)
            self.process.setProcessChannelMode(QProcess.MergedChannels)
            self.process.readyReadStandardOutput.connect(self.handle_process_output)
            self.process.finished.connect(self.on_brute_force_finished)

            self.process.start(sys.executable, [script_name])

            self.log_output.append("[Перебор] Скрипт запущен. Переключитесь в игру и нажмите Backspace.")
            self.brute_force_btn.setEnabled(False)

        except Exception as e:
            self.log_output.append(f"[Ошибка] Перебор: {str(e)}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка запуска перебора:\n{str(e)}")

    def on_brute_force_finished(self, exit_code, exit_status):
        self.process = None
        if exit_code == 0:
            self.log_output.append("[Перебор] Успешно завершен.")
            self.progress_bar.setValue(100)
            QMessageBox.information(self, "Успех", "Перебор комбинаций завершен успешно!")
        else:
            self.log_output.append(f"[Ошибка] Перебор завершен с кодом {exit_code}.")
            QMessageBox.critical(self, "Ошибка", f"Перебор завершен с ошибкой (код {exit_code}).")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CodeConfigurator()
    window.show()
    sys.exit(app.exec_())