# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec для Speech Manager
Создает один .exe файл со всеми зависимостями
"""

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],  # Добавляем текущую директорию для поиска модулей
    binaries=[],
    datas=[
        # Не копируем config.json - приложение создаст его автоматически при первом запуске
        # config.json.example создается скриптом create_config_example.py перед сборкой
    ],
    hiddenimports=[
        # PyQt5
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        
        # Audio
        'sounddevice',
        'numpy',
        
        # Speech
        'speech_recognition',
        
        # Наши модули
        'config',
        'state',
        'listner',
        'subtitle_speach',
        'subtitle_speach.status_colors',
        'audio_recorder',
        'logger_config',
        'threading_manager',
        'settings_window',
        'i18n',  # Модуль локализации
        
        # Windows
        'win32api',
        'win32con',
        'pywintypes',
        
        # Utils
        'keyboard',
        'pyperclip',
        'tenacity',
        'pyglet',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Исключаем тяжелые ML библиотеки
        'torch',
        'tensorflow',
        'pandas',
        'scipy',
        'sklearn',
        'matplotlib',
        'PIL',
        'cv2',
        
        # Jupyter
        'IPython',
        'jupyter',
        'notebook',
        
        # Лишние Qt модули
        'PyQt5.QtBluetooth',
        'PyQt5.QtDBus',
        'PyQt5.QtDesigner',
        'PyQt5.QtHelp',
        'PyQt5.QtLocation',
        'PyQt5.QtMultimedia',
        'PyQt5.QtNetwork',
        'PyQt5.QtNfc',
        'PyQt5.QtOpenGL',
        'PyQt5.QtPositioning',
        'PyQt5.QtPrintSupport',
        'PyQt5.QtQml',
        'PyQt5.QtQuick',
        'PyQt5.QtSensors',
        'PyQt5.QtSerialPort',
        'PyQt5.QtSql',
        'PyQt5.QtSvg',
        'PyQt5.QtTest',
        'PyQt5.QtWebChannel',
        'PyQt5.QtWebSockets',
        'PyQt5.QtXml',
        
        # Прочее
        'tkinter',
        'pytest',
        'setuptools',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SpeechManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Без консоли
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
