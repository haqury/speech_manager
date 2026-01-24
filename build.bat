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

REM Создаем config.json.example из config.json (без ключей)
echo 📝 Создание config.json.example...
python create_config_example.py
if errorlevel 1 (
    echo ⚠️  Не удалось создать config.json.example, продолжаем сборку...
)
echo.

REM Копируем config.json.example в dist для пользователей
echo 📋 Копирование config.json.example в dist...
if exist config.json.example (
    if not exist dist mkdir dist
    copy /Y config.json.example dist\config.json.example >nul
    echo ✅ config.json.example скопирован в dist
) else (
    echo ⚠️  config.json.example не найден, пропускаем копирование...
)
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
