"""
Logging configuration for Speech Manager.

Provides centralized logging setup with both file and console handlers.
"""
import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    log_file: str = 'speech_manager.log',
    level: int = logging.INFO,
    log_dir: Optional[str] = None
) -> logging.Logger:
    """
    Configure logging for the application.
    
    Args:
        log_file: Name of the log file
        level: Logging level (default: INFO)
        log_dir: Directory for log files (default: current directory)
        
    Returns:
        Configured root logger
    """
    # Create log directory if specified
    if log_dir:
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True, parents=True)
        log_file_path = log_path / log_file
    else:
        log_file_path = Path(log_file)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler
    file_handler = logging.FileHandler(
        log_file_path,
        encoding='utf-8',
        mode='a'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # Add handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
