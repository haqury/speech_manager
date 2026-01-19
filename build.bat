@echo off
REM Скрипт для сборки SpeechManager.exe
REM Использует PyInstaller

echo ============================================================
echo 🔨 Speech Manager - Сборка .exe
echo ============================================================
echo.

REM Проверяем PyInstaller
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo ❌ PyInstaller не установлен!
    echo 📦 Установите: pip install pyinstaller
    pause
    exit /b 1
)

echo ✅ PyInstaller найден
echo.

REM Очистка старых файлов
echo 🧹 Очистка старых файлов...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__
echo.

REM Сборка
echo 🔨 Запуск PyInstaller...
pyinstaller --clean build_exe.spec

if errorlevel 1 (
    echo.
    echo ❌ Ошибка при сборке!
    pause
    exit /b 1
)

REM Проверка результата
if exist dist\SpeechManager.exe (
    echo.
    echo ============================================================
    echo ✅ Сборка завершена успешно!
    echo ============================================================
    echo.
    echo 📦 Файл: dist\SpeechManager.exe
    echo.
    dir dist\SpeechManager.exe | find "SpeechManager.exe"
    echo.
    echo 🚀 Для запуска: dist\SpeechManager.exe
    echo ============================================================
) else (
    echo.
    echo ❌ Файл не найден: dist\SpeechManager.exe
)

echo.
pause
