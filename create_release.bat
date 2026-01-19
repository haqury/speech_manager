@echo off
REM ============================================================
REM Speech Manager - Скрипт создания GitHub Release
REM ============================================================
REM
REM Использование:
REM   create_release.bat [version]
REM
REM Пример:
REM   create_release.bat 1.0.0
REM
REM Требования:
REM   - git
REM   - gh (GitHub CLI) - https://cli.github.com/
REM   - Собранный SpeechManager.exe в dist/
REM ============================================================

setlocal enabledelayedexpansion

REM Получаем версию из параметра или из файла VERSION
if "%~1"=="" (
    if exist VERSION (
        set /p VERSION=<VERSION
        echo Используется версия из VERSION: !VERSION!
    ) else (
        echo ❌ Ошибка: Версия не указана и файл VERSION не найден
        echo.
        echo Использование: create_release.bat [version]
        echo Пример: create_release.bat 1.0.0
        pause
        exit /b 1
    )
) else (
    set VERSION=%~1
    echo Используется версия: !VERSION!
)

echo.
echo ============================================================
echo 🚀 Создание GitHub Release v!VERSION!
echo ============================================================
echo.

REM Проверяем что мы в правильной директории
if not exist "main.py" (
    echo ❌ Ошибка: Запустите скрипт из корня проекта
    pause
    exit /b 1
)

REM Проверяем наличие .exe
if not exist "dist\SpeechManager.exe" (
    echo ❌ Ошибка: dist\SpeechManager.exe не найден
    echo.
    echo Сначала соберите .exe файл:
    echo   build.bat
    pause
    exit /b 1
)

REM Проверяем git
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git не установлен
    echo 📥 Установите: https://git-scm.com/downloads
    pause
    exit /b 1
)

REM Проверяем GitHub CLI
gh --version >nul 2>&1
if errorlevel 1 (
    echo ❌ GitHub CLI (gh) не установлен
    echo 📥 Установите: https://cli.github.com/
    pause
    exit /b 1
)

REM Проверяем авторизацию в GitHub
gh auth status >nul 2>&1
if errorlevel 1 (
    echo ❌ Не авторизованы в GitHub CLI
    echo.
    echo Выполните:
    echo   gh auth login
    pause
    exit /b 1
)

echo ✅ Все проверки пройдены
echo.

REM Показываем статус git
echo 📊 Git статус:
git status --short
echo.

REM Спрашиваем подтверждение
echo Будет создан GitHub Release:
echo   - Версия: v!VERSION!
echo   - Файл: dist\SpeechManager.exe
echo.
set /p CONFIRM="Продолжить? (y/N): "
if /i not "!CONFIRM!"=="y" (
    echo Отменено пользователем
    pause
    exit /b 0
)

echo.
echo ============================================================
echo 🔨 Шаг 1/4: Проверка изменений
echo ============================================================

REM Проверяем что нет незакоммиченных изменений
git diff-index --quiet HEAD --
if errorlevel 1 (
    echo ⚠️  Найдены незакоммиченные изменения
    echo.
    set /p COMMIT="Закоммитить изменения? (y/N): "
    if /i "!COMMIT!"=="y" (
        git add .
        git commit -m "Release v!VERSION!"
        echo ✅ Изменения закоммичены
    ) else (
        echo ❌ Отменено: есть незакоммиченные изменения
        pause
        exit /b 1
    )
) else (
    echo ✅ Нет незакоммиченных изменений
)

echo.
echo ============================================================
echo 🏷️  Шаг 2/4: Создание Git тега
echo ============================================================

REM Проверяем что тег еще не существует
git tag -l | findstr /C:"v!VERSION!" >nul
if not errorlevel 1 (
    echo ⚠️  Тег v!VERSION! уже существует
    echo.
    set /p DELETE_TAG="Удалить существующий тег? (y/N): "
    if /i "!DELETE_TAG!"=="y" (
        git tag -d v!VERSION!
        git push origin :refs/tags/v!VERSION! 2>nul
        echo ✅ Старый тег удален
    ) else (
        echo ❌ Отменено
        pause
        exit /b 1
    )
)

REM Создаем тег
git tag -a v!VERSION! -m "Release v!VERSION!"
if errorlevel 1 (
    echo ❌ Ошибка создания тега
    pause
    exit /b 1
)
echo ✅ Тег v!VERSION! создан

echo.
echo ============================================================
echo 📤 Шаг 3/4: Push в GitHub
echo ============================================================

REM Пушим коммиты
git push
if errorlevel 1 (
    echo ❌ Ошибка при push коммитов
    pause
    exit /b 1
)
echo ✅ Коммиты отправлены

REM Пушим теги
git push --tags
if errorlevel 1 (
    echo ❌ Ошибка при push тегов
    pause
    exit /b 1
)
echo ✅ Теги отправлены

echo.
echo ============================================================
echo 🎉 Шаг 4/4: Создание GitHub Release
echo ============================================================

REM Читаем changelog для этой версии (первая секция)
set NOTES=Release v!VERSION!

REM Создаем release
gh release create v!VERSION! ^
    dist\SpeechManager.exe ^
    --title "Speech Manager v!VERSION!" ^
    --notes "!NOTES!" ^
    --latest

if errorlevel 1 (
    echo ❌ Ошибка создания Release
    pause
    exit /b 1
)

echo.
echo ============================================================
echo ✅ GitHub Release успешно создан!
echo ============================================================
echo.
echo 📦 Версия: v!VERSION!
echo 🔗 Release: https://github.com/haqury/speech_manager/releases/tag/v!VERSION!
echo.
echo Что было сделано:
echo   ✅ Изменения закоммичены
echo   ✅ Создан тег v!VERSION!
echo   ✅ Отправлено в GitHub
echo   ✅ Создан GitHub Release
echo   ✅ Загружен SpeechManager.exe
echo.

pause
