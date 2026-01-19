@echo off
REM ============================================================
REM Speech Manager - Упаковка релиза
REM ============================================================
REM
REM Создает архивы для GitHub Release:
REM   1. SpeechManager-vX.X.X-win64.zip       - Готовый .exe для пользователей
REM   2. SpeechManager-vX.X.X-source.zip      - Исходный код для разработчиков
REM
REM Требования:
REM   - PowerShell (встроен в Windows)
REM   - Собранный SpeechManager.exe в dist/
REM ============================================================

setlocal enabledelayedexpansion

REM Получаем версию из файла VERSION
if exist VERSION (
    set /p VERSION=<VERSION
    echo Версия: !VERSION!
) else (
    echo ❌ Файл VERSION не найден
    pause
    exit /b 1
)

echo.
echo ============================================================
echo 📦 Упаковка релиза v!VERSION!
echo ============================================================
echo.

REM Проверяем наличие .exe
if not exist "dist\SpeechManager.exe" (
    echo ❌ Ошибка: dist\SpeechManager.exe не найден
    echo.
    echo Сначала соберите .exe:
    echo   build.bat
    pause
    exit /b 1
)

REM Создаем папку для релизов
if not exist "releases" mkdir releases

REM Имена архивов
set EXE_ZIP=releases\SpeechManager-v!VERSION!-win64.zip
set SRC_ZIP=releases\SpeechManager-v!VERSION!-source.zip

echo 📦 Будут созданы:
echo   1. !EXE_ZIP!
echo   2. !SRC_ZIP!
echo.

REM Удаляем старые архивы если есть
if exist "!EXE_ZIP!" del /f /q "!EXE_ZIP!"
if exist "!SRC_ZIP!" del /f /q "!SRC_ZIP!"

REM ============================================================
echo 📦 Шаг 1/2: Упаковка .exe релиза
echo ============================================================

REM Создаем временную папку для .exe релиза
if exist "temp_exe_release" rmdir /s /q temp_exe_release
mkdir temp_exe_release

REM Копируем файлы для пользователей
echo Копирование файлов...
copy "dist\SpeechManager.exe" "temp_exe_release\" >nul
copy "config.json" "temp_exe_release\config.json.example" >nul
copy "README.md" "temp_exe_release\" >nul
copy "CHANGELOG.md" "temp_exe_release\" >nul
copy "LICENSE" "temp_exe_release\" >nul

REM Создаем README для релиза
echo # Speech Manager v!VERSION! - Windows Release> "temp_exe_release\README_RELEASE.txt"
echo.>> "temp_exe_release\README_RELEASE.txt"
echo ## Быстрый старт>> "temp_exe_release\README_RELEASE.txt"
echo.>> "temp_exe_release\README_RELEASE.txt"
echo 1. Запустите SpeechManager.exe>> "temp_exe_release\README_RELEASE.txt"
echo 2. При первом запуске создастся config.json>> "temp_exe_release\README_RELEASE.txt"
echo 3. Нажмите Ctrl+Shift+Win+F5 для начала распознавания>> "temp_exe_release\README_RELEASE.txt"
echo.>> "temp_exe_release\README_RELEASE.txt"
echo ## Содержимое архива>> "temp_exe_release\README_RELEASE.txt"
echo.>> "temp_exe_release\README_RELEASE.txt"
echo - SpeechManager.exe      - Главный исполняемый файл>> "temp_exe_release\README_RELEASE.txt"
echo - config.json.example    - Пример конфигурации>> "temp_exe_release\README_RELEASE.txt"
echo - README.md              - Полная документация>> "temp_exe_release\README_RELEASE.txt"
echo - CHANGELOG.md           - История изменений>> "temp_exe_release\README_RELEASE.txt"
echo - LICENSE                - Лицензия MIT>> "temp_exe_release\README_RELEASE.txt"
echo.>> "temp_exe_release\README_RELEASE.txt"
echo ## Системные требования>> "temp_exe_release\README_RELEASE.txt"
echo.>> "temp_exe_release\README_RELEASE.txt"
echo - Windows 10/11>> "temp_exe_release\README_RELEASE.txt"
echo - Микрофон для распознавания речи>> "temp_exe_release\README_RELEASE.txt"
echo - Интернет для работы Google Speech API>> "temp_exe_release\README_RELEASE.txt"
echo.>> "temp_exe_release\README_RELEASE.txt"
echo ## Ссылки>> "temp_exe_release\README_RELEASE.txt"
echo.>> "temp_exe_release\README_RELEASE.txt"
echo - GitHub: https://github.com/haqury/speech_manager>> "temp_exe_release\README_RELEASE.txt"
echo - Документация: https://github.com/haqury/speech_manager/blob/main/README.md>> "temp_exe_release\README_RELEASE.txt"
echo - Проблемы: https://github.com/haqury/speech_manager/issues>> "temp_exe_release\README_RELEASE.txt"

REM Создаем архив с помощью PowerShell
echo Создание архива...
powershell -Command "Compress-Archive -Path 'temp_exe_release\*' -DestinationPath '!EXE_ZIP!' -Force"

if errorlevel 1 (
    echo ❌ Ошибка создания архива
    rmdir /s /q temp_exe_release
    pause
    exit /b 1
)

REM Удаляем временную папку
rmdir /s /q temp_exe_release

echo ✅ Создан: !EXE_ZIP!

REM Показываем размер
for %%A in ("!EXE_ZIP!") do (
    set SIZE=%%~zA
    set /a SIZE_MB=!SIZE! / 1048576
    echo    Размер: !SIZE_MB! MB
)

echo.

REM ============================================================
echo 📦 Шаг 2/2: Упаковка исходного кода
echo ============================================================

REM Создаем временную папку для исходников
if exist "temp_src_release" rmdir /s /q temp_src_release
mkdir temp_src_release
mkdir temp_src_release\SpeechManager

REM Копируем исходники
echo Копирование исходного кода...

REM Основные файлы
copy "*.py" "temp_src_release\SpeechManager\" >nul 2>&1
copy "*.md" "temp_src_release\SpeechManager\" >nul 2>&1
copy "*.txt" "temp_src_release\SpeechManager\" >nul 2>&1
copy "*.json" "temp_src_release\SpeechManager\" >nul 2>&1
copy "*.bat" "temp_src_release\SpeechManager\" >nul 2>&1
copy "*.spec" "temp_src_release\SpeechManager\" >nul 2>&1
copy "LICENSE" "temp_src_release\SpeechManager\" >nul 2>&1
copy "VERSION" "temp_src_release\SpeechManager\" >nul 2>&1

REM Папки с кодом
xcopy /E /I /Q "config" "temp_src_release\SpeechManager\config\" >nul 2>&1
xcopy /E /I /Q "state" "temp_src_release\SpeechManager\state\" >nul 2>&1
xcopy /E /I /Q "listner" "temp_src_release\SpeechManager\listner\" >nul 2>&1
xcopy /E /I /Q "subtitle_speach" "temp_src_release\SpeechManager\subtitle_speach\" >nul 2>&1

REM Создаем README для исходников
echo # Speech Manager v!VERSION! - Source Code> "temp_src_release\SpeechManager\README_SOURCE.txt"
echo.>> "temp_src_release\SpeechManager\README_SOURCE.txt"
echo ## Установка>> "temp_src_release\SpeechManager\README_SOURCE.txt"
echo.>> "temp_src_release\SpeechManager\README_SOURCE.txt"
echo 1. Установите Python 3.11+>> "temp_src_release\SpeechManager\README_SOURCE.txt"
echo 2. Установите зависимости:>> "temp_src_release\SpeechManager\README_SOURCE.txt"
echo    pip install -r requirements.txt>> "temp_src_release\SpeechManager\README_SOURCE.txt"
echo.>> "temp_src_release\SpeechManager\README_SOURCE.txt"
echo ## Запуск>> "temp_src_release\SpeechManager\README_SOURCE.txt"
echo.>> "temp_src_release\SpeechManager\README_SOURCE.txt"
echo python main.py>> "temp_src_release\SpeechManager\README_SOURCE.txt"
echo.>> "temp_src_release\SpeechManager\README_SOURCE.txt"
echo ## Сборка .exe>> "temp_src_release\SpeechManager\README_SOURCE.txt"
echo.>> "temp_src_release\SpeechManager\README_SOURCE.txt"
echo build.bat>> "temp_src_release\SpeechManager\README_SOURCE.txt"
echo.>> "temp_src_release\SpeechManager\README_SOURCE.txt"
echo Подробности см. в BUILD.md>> "temp_src_release\SpeechManager\README_SOURCE.txt"

REM Создаем архив
echo Создание архива...
powershell -Command "Compress-Archive -Path 'temp_src_release\SpeechManager' -DestinationPath '!SRC_ZIP!' -Force"

if errorlevel 1 (
    echo ❌ Ошибка создания архива
    rmdir /s /q temp_src_release
    pause
    exit /b 1
)

REM Удаляем временную папку
rmdir /s /q temp_src_release

echo ✅ Создан: !SRC_ZIP!

REM Показываем размер
for %%A in ("!SRC_ZIP!") do (
    set SIZE=%%~zA
    set /a SIZE_MB=!SIZE! / 1048576
    echo    Размер: !SIZE_MB! MB
)

echo.
echo ============================================================
echo ✅ Упаковка завершена!
echo ============================================================
echo.
echo Созданные файлы:
echo.
dir /b releases\*.zip
echo.
echo Загрузите эти файлы на GitHub Release:
echo https://github.com/haqury/speech_manager/releases/tag/v!VERSION!
echo.

pause
