import sys
import zipfile
import yaml
import tempfile
import shutil
from datetime import datetime
import calendar
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QLineEdit, QVBoxLayout, QWidget

class ShellEmulator(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.username = config['username']
        self.hostname = config['hostname']
        self.vfs_path = config['vfs_path']
        self.startup_script = config['startup_script']

        # Текущая рабочая директория в виртуальной файловой системе
        self.current_dir = ""
        self.zip_file = zipfile.ZipFile(self.vfs_path, 'r')
        self.empty_dirs = []  # Список для пустых директорий

        # GUI setup
        self.initUI()

        # Выполнение стартового скрипта
        self.run_startup_script()

    def initUI(self):
        self.setWindowTitle("Shell Emulator")
        self.setGeometry(100, 100, 800, 600)

        self.output_area = QTextEdit(self)
        self.output_area.setReadOnly(True)

        self.input_line = QLineEdit(self)
        self.input_line.returnPressed.connect(self.process_command)

        layout = QVBoxLayout()
        layout.addWidget(self.output_area)
        layout.addWidget(self.input_line)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def run_startup_script(self):
        if self.startup_script:
            try:
                with open(self.startup_script, 'r') as f:
                    commands = f.readlines()
                    for command in commands:
                        self.execute_command(command.strip())
            except FileNotFoundError:
                self.output_area.append(f"Startup script '{self.startup_script}' not found.")

    def process_command(self):
        command = self.input_line.text().strip()
        self.input_line.clear()
        self.execute_command(command)

    def execute_command(self, command):
        # Отображаем строку приглашения и команду
        prompt = f"{self.username}@{self.hostname}:/{self.current_dir}$ {command}"
        self.output_area.append(prompt)

        # Проверка и выполнение команды
        if command.startswith("ls"):
            result = self.ls()
            self.output_area.append(result)
        elif command.startswith("cd"):
            path = command.split(" ", 1)[1] if " " in command else ""
            result = self.cd(path)
            self.output_area.append(result)
        elif command.startswith("exit"):
            self.close()
        elif command.startswith("cal"):
            result = self.cal()
            self.output_area.append(result)
        elif command.startswith("tac"):
            path = command.split(" ", 1)[1] if " " in command else ""
            result = self.tac(path)
            self.output_area.append(result)
        elif command.startswith("date"):
            result = self.date()
            self.output_area.append(result)
        else:
            self.output_area.append(f"Command not found: {command}")

    def ls(self):
        directory = self.current_dir.strip("/")
        if directory:
            directory += "/"

        items = set()

        # Добавляем содержимое ZIP-файла
        for name in self.zip_file.namelist():
            if name.startswith(directory) and name != directory:
                relative_path = name[len(directory):].split('/')[0]
                if relative_path:
                    items.add(relative_path)

        # Добавляем пустые директории
        for empty_dir in self.empty_dirs:
            if empty_dir.startswith(directory) and empty_dir != directory:
                relative_path = empty_dir[len(directory):].split('/')[0]
                if relative_path:
                    items.add(relative_path)

        if items:
            return "\n".join(sorted(items))
        else:
            return "ls: no such file or directory"

    def cd(self, path):
        if path == "..":
            self.current_dir = "/".join(self.current_dir.split("/")[:-1])
            return f"Moved to directory: {self.current_dir}"
        elif path == "." or not path:
            return "cd: no operation"
        else:
            potential_dir = f"{self.current_dir}/{path}".strip("/")
            if any(name.startswith(potential_dir + "/") for name in self.zip_file.namelist()) or potential_dir + "/" in self.empty_dirs:
                self.current_dir = potential_dir
                return f"Changed directory to {self.current_dir}"
            else:
                return f"cd: no such file or directory: {path}"

    def cal(self):
        try:
            return calendar.TextCalendar().formatmonth(datetime.now().year, datetime.now().month)
        except Exception as e:
            return f"cal: error: {e}"

    def tac(self, path):
        target_file = f"{self.current_dir}/{path}".strip("/")
        try:
            with self.zip_file.open(target_file) as file:
                # Чтение содержимого файла и разделение его на строки
                content = file.read().decode('utf-8')
                lines = content.splitlines()

                # Переворачивание строк
                reversed_lines = "\n".join(reversed(lines))

                return reversed_lines
        except KeyError:
            return f"tac: no such file: {target_file}"
        except UnicodeDecodeError:
            return f"tac: error decoding file {path}: invalid UTF-8 content"
        except Exception as e:
            return f"tac: error reading file {path}: {e}"

    def date(self):
        try:
            current_time = datetime.now().strftime("%a %b %d %H:%M:%S %Z %Y")
            return current_time
        except Exception as e:
            return f"date: error: {e}"

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Shell Emulator")
    parser.add_argument('--username', required=True, help="Имя пользователя")
    parser.add_argument('--vfs', required=True, help="Путь к архиву виртуальной файловой системы")
    parser.add_argument('--script', required=False, help="Путь к стартовому скрипту", default=None)

    args = parser.parse_args()

    config = {
        'username': args.username,
        'hostname': 'localhost',
        'vfs_path': args.vfs,
        'startup_script': args.script
    }

    app = QApplication(sys.argv)
    shell = ShellEmulator(config)
    shell.show()
    sys.exit(app.exec_())
