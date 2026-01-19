"""
Модуль для управления цветами статусов в UI.
Обеспечивает визуальную обратную связь о текущем состоянии приложения.
"""

# Цвета для разных статусов
STATUS_COLORS = {
    'listening': '#00FF00',      # Зеленый - слушаем речь
    'recognizing': '#FFA500',    # Оранжевый - распознаем через API
    'on': '#00FF00',             # Зеленый - активно
    'off': '#888888',            # Серый - выключено
    'error': '#FF0000',          # Красный - ошибка
}

def get_status_style(status: str, font_size: int = 30) -> str:
    """
    Возвращает стиль CSS для статусного лейбла.
    
    Args:
        status: Ключ статуса ('listening', 'recognizing', 'on', 'off', 'error')
        font_size: Размер шрифта в пикселях
        
    Returns:
        Строка со стилем CSS
    """
    color = STATUS_COLORS.get(status, STATUS_COLORS['off'])
    return f"""
        QLabel {{
            font-family: 'Consolas';
            background-color: rgba(0, 0, 0, 40);
            color: {color};
            font-size: {font_size}px;
        }}
    """
