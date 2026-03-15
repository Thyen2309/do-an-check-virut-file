"""Configuration management"""

import json
import os
from pathlib import Path


class Config:
    """Application configuration manager"""
    
    DEFAULT_CONFIG = {
        'theme': 'light',
        'auto_scan': False,
        'scan_on_open': True,
        'enable_logging': True,
        'database_path': './data/scanner.db',
        'log_directory': './logs',
        'malware_db_path': './assets/dangerous_hashes.json',
        'enable_quarantine': True,
        'quarantine_directory': './quarantine',
        'enable_cloud_updates': False,
        'update_interval': 86400  # 24 hours in seconds
    }
    
    def __init__(self, config_path: str = 'config.json'):
        """
        Initialize configuration
        
        Args:
            config_path: Path to config JSON file
        """
        self.config_path = config_path
        self.config = self.DEFAULT_CONFIG.copy()
        self.load()
    
    def load(self) -> None:
        """Load configuration from file"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    user_config = json.load(f)
                    self.config.update(user_config)
            except Exception as e:
                print(f'Error loading config: {e}')
    
    def save(self) -> None:
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f'Error saving config: {e}')
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value) -> None:
        """Set configuration value"""
        self.config[key] = value
    
    def ensure_directories(self) -> None:
        """Ensure all required directories exist"""
        directories = [
            self.get('log_directory'),
            self.get('quarantine_directory'),
            os.path.dirname(self.get('database_path'))
        ]
        
        for dir_path in directories:
            if dir_path:
                Path(dir_path).mkdir(parents=True, exist_ok=True)
