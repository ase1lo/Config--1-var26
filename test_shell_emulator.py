import zipfile
import tempfile
import os
from io import BytesIO
from datetime import datetime
import calendar
import sys
from shell_emulator import ShellEmulator
from PyQt5.QtWidgets import QApplication


def create_temp_zip():
    """Создание временного ZIP-архива с тестовыми данными."""
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        zip_file.writestr('file1.txt', 'Hello, world!')
        zip_file.writestr('file2.txt', 'This is a second file.')
        zip_file.writestr('dir1/file3.txt', 'Inside a directory')
    zip_buffer.seek(0)
    return zip_buffer


def test_ls():
    print("\nTesting 'ls' command:")

    # Тест 1: Проверка вывода для пустой директории
    with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
        temp_file_path = temp_file.name
        with zipfile.ZipFile(temp_file_path, 'w') as zipf:
            pass  # Пустой архив
    app = QApplication([])  # Создаем QApplication
    shell = ShellEmulator({'username': 'test_user', 'hostname': 'localhost', 'vfs_path': temp_file_path, 'startup_script': None})
    result = shell.ls()
    print(result)
    assert result == "ls: no such file or directory", "Expected empty directory message"
    
    # Тест 2: Проверка вывода с несколькими файлами в директории
    with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
        temp_file_path = temp_file.name
        with zipfile.ZipFile(temp_file_path, 'w') as zipf:
            zipf.writestr("file1.txt", "Test content")
            zipf.writestr("file2.txt", "Another test")
    shell = ShellEmulator({'username': 'test_user', 'hostname': 'localhost', 'vfs_path': temp_file_path, 'startup_script': None})
    result = shell.ls()
    print(result)
    assert "file1.txt" in result and "file2.txt" in result, "Expected files to be listed"
    
    # Тест 3: Проверка вывода с поддиректориями
    with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
        temp_file_path = temp_file.name
        with zipfile.ZipFile(temp_file_path, 'w') as zipf:
            zipf.writestr("dir1/file1.txt", "File in directory")
            zipf.writestr("dir2/file2.txt", "Another file")
    shell = ShellEmulator({'username': 'test_user', 'hostname': 'localhost', 'vfs_path': temp_file_path, 'startup_script': None})
    result = shell.ls()
    print(result)
    assert "dir1" in result and "dir2" in result, "Expected directories to be listed"

    print("'ls' tests passed!")



def test_cd():
    print("\nTesting 'cd' command:")

    # Тест 1: Переход в существующую директорию
    with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
        temp_file_path = temp_file.name
        with zipfile.ZipFile(temp_file_path, 'w') as zipf:
            zipf.writestr("dir1/file1.txt", "File in directory")
    app = QApplication([])
    shell = ShellEmulator({'username': 'test_user', 'hostname': 'localhost', 'vfs_path': temp_file_path, 'startup_script': None})
    result = shell.cd("dir1")
    print(result)
    assert result == "Changed directory to dir1", "Expected successful directory change"

    # Тест 2: Переход в несуществующую директорию
    result = shell.cd("nonexistent_dir")
    print(result)
    assert result == "cd: no such file or directory: nonexistent_dir", "Expected error for nonexistent directory"

    # Тест 3: Переход в родительскую директорию
    result = shell.cd("..")
    print(result)
    assert result == "Moved to directory: ", "Expected move to parent directory"

    print("'cd' tests passed!")




def test_cal():
    print("\nTesting 'cal' command:")
    with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
        temp_file_path = temp_file.name
        with zipfile.ZipFile(temp_file_path, 'w') as zipf:
            pass  # Пустой архив
    # Тест 1: Проверка правильности вывода текущего месяца
    app = QApplication([])  # Создаем QApplication
    shell = ShellEmulator({'username': 'test_user', 'hostname': 'localhost', 'vfs_path': temp_file_path, 'startup_script': None})
    result = shell.cal()
    print(result)
    current_month = datetime.now().strftime("%B %Y")
    assert current_month in result, f"Expected current month {current_month} to be in the output"

    # Тест 2: Проверка корректности работы после выполнения других команд
    shell.execute_command("ls")  # Выполняем команду ls для теста
    result = shell.cal()
    print(result)
    assert current_month in result, f"Expected current month {current_month} to be in the output after other command"

    # Тест 3: Проверка при пустом архиве (не должно вызывать ошибок)

    shell = ShellEmulator({'username': 'test_user', 'hostname': 'localhost', 'vfs_path': temp_file_path, 'startup_script': None})
    result = shell.cal()
    print(result)
    assert current_month in result, "Expected current month to be in the output"

    print("'cal' tests passed!")



def test_tac():
    print("\nTesting 'tac' command:")

    # Тест 1: Вывод содержимого файла в обратном порядке
    with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
        temp_file_path = temp_file.name
        with zipfile.ZipFile(temp_file_path, 'w') as zipf:
            zipf.writestr("file1.txt", "Line 1\nLine 2\nLine 3")
    app = QApplication([])
    shell = ShellEmulator({'username': 'test_user', 'hostname': 'localhost', 'vfs_path': temp_file_path, 'startup_script': None})
    result = shell.tac("file1.txt")
    print(result)
    assert "Line 3" in result and "Line 1" in result, "Expected content to be in reverse order"

    # Тест 2: Попытка вывода несуществующего файла
    result = shell.tac("nonexistent_file.txt")
    print(result)
    assert result == "tac: no such file: nonexistent_file.txt", "Expected error for nonexistent file"

    # Тест 3: Попытка чтения файла с некорректным содержимым (не UTF-8)
    with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
        temp_file_path = temp_file.name
        with zipfile.ZipFile(temp_file_path, 'w') as zipf:
            zipf.writestr("file2.txt", b'\x80\x81\x82')  # Некорректные байты
    shell = ShellEmulator({'username': 'test_user', 'hostname': 'localhost', 'vfs_path': temp_file_path, 'startup_script': None})
    result = shell.tac("file2.txt")
    print(result)
    assert "tac: error decoding file" in result, "Expected decoding error message"

    print("'tac' tests passed!")



def test_date():
    print("\nTesting 'date' command:")

    # Тест 1: Проверка правильности текущего времени
    with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
        temp_file_path = temp_file.name
        with zipfile.ZipFile(temp_file_path, 'w') as zipf:
            pass  # Пустой архив
    app = QApplication([])  # Создаем QApplication
    shell = ShellEmulator({'username': 'test_user', 'hostname': 'localhost', 'vfs_path': temp_file_path, 'startup_script': None})
    result = shell.date()
    print(result)
    current_time = datetime.now().strftime("%a %b %d %H:%M:%S %Z %Y")
    assert result.strip() == current_time.strip(), "Date should match current system time"

    # Тест 2: Проверка работы с пустым архивом
    result = shell.date()
    print(result)
    assert result.strip() == current_time.strip(), "Date should match current system time even with an empty archive"

    # Тест 3: Проверка работы после выполнения команды 'ls'
    shell.execute_command("ls")
    result = shell.date()
    print(result)
    assert result.strip() == current_time.strip(), "Date should match current system time after other commands"

    print("'date' tests passed!")




def run_tests():
    try:
        test_ls()
        test_cd()
        test_cal()
        test_tac()
        test_date()
        print("\nAll tests passed successfully!")
    except AssertionError as e:
        print(f"\nTest failed: {e}")

run_tests()
