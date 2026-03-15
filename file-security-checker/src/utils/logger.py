"""Logging configuration"""

import logging
import os
from datetime import datetime


def setup_logger(log_directory: str = './logs', name: str = 'file_security_checker'):
    """
    Setup logger for the application
    
    Args:
        log_directory: Directory to store logs
        name: Logger name
        
    Returns:
        Logger instance
    """
    # Create log directory if it doesn't exist
    os.makedirs(log_directory, exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # File handler
    log_file = os.path.join(
        log_directory,
        f'scan_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    )
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
