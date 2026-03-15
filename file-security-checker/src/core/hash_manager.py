"""
Hash Manager Module
Calculate and verify file hashes, manage malware hash database
"""

import hashlib
import json
import os
from typing import Tuple


class HashManager:
    """Manage file hashing and hash database operations"""
    
    def __init__(self, dangerous_hashes_path: str = None):
        """
        Initialize Hash Manager
        
        Args:
            dangerous_hashes_path: Path to dangerous hashes JSON file
        """
        self.dangerous_hashes = {}
        self.whitelist_hashes = set()
        
        if dangerous_hashes_path:
            self.load_dangerous_hashes(dangerous_hashes_path)
    
    def calculate_file_hash(self, file_path: str, algorithm: str = 'sha256') -> str:
        """
        Tính hash của file
        
        Args:
            file_path: Đường dẫn file
            algorithm: Thuật toán hash ('sha256', 'sha1', 'md5')
            
        Returns:
            Hash string (hex format)
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If algorithm not supported
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'File not found: {file_path}')
        
        if algorithm not in ['sha256', 'sha1', 'md5']:
            raise ValueError(f'Unsupported algorithm: {algorithm}')
        
        hasher = hashlib.new(algorithm)
        
        try:
            with open(file_path, 'rb') as f:
                # Read file in chunks to save memory
                for chunk in iter(lambda: f.read(4096), b''):
                    hasher.update(chunk)
            
            return hasher.hexdigest()
        
        except IOError as e:
            raise ValueError(f'Error reading file: {e}')
    
    def calculate_multi_hash(self, file_path: str) -> dict:
        """
        Tính multiple hashes cho file
        
        Args:
            file_path: Đường dẫn file
            
        Returns:
            dict với các hash values
        """
        return {
            'sha256': self.calculate_file_hash(file_path, 'sha256'),
            'sha1': self.calculate_file_hash(file_path, 'sha1'),
            'md5': self.calculate_file_hash(file_path, 'md5')
        }
    
    def is_dangerous_hash(self, file_hash: str) -> Tuple[bool, dict]:
        """
        Kiểm tra hash có trong malware database không
        
        Args:
            file_hash: File hash to check
            
        Returns:
            (is_dangerous, threat_info_dict)
        """
        file_hash = file_hash.lower()
        
        if file_hash in self.dangerous_hashes:
            return True, self.dangerous_hashes[file_hash]
        
        return False, {}
    
    def is_whitelisted_hash(self, file_hash: str) -> bool:
        """
        Kiểm tra hash có trong whitelist không
        
        Args:
            file_hash: File hash to check
            
        Returns:
            True nếu whitelisted
        """
        return file_hash.lower() in self.whitelist_hashes
    
    def add_dangerous_hash(self, file_hash: str, threat_info: dict) -> None:
        """
        Thêm hash vào dangerous database
        
        Args:
            file_hash: Hash value
            threat_info: Dictionary với threat information
        """
        self.dangerous_hashes[file_hash.lower()] = threat_info
    
    def add_whitelist_hash(self, file_hash: str) -> None:
        """
        Thêm hash vào whitelist
        
        Args:
            file_hash: Hash value
        """
        self.whitelist_hashes.add(file_hash.lower())
    
    def load_dangerous_hashes(self, json_path: str) -> None:
        """
        Load dangerous hashes từ JSON file
        
        Args:
            json_path: Path to JSON file
        """
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
                # Expected format: {"hash1": {"threat_name": "...", "severity": ...}, ...}
                self.dangerous_hashes = data
        
        except FileNotFoundError:
            print(f'Warning: Dangerous hashes file not found: {json_path}')
        except json.JSONDecodeError:
            print(f'Warning: Invalid JSON in {json_path}')
    
    def save_dangerous_hashes(self, json_path: str) -> None:
        """
        Lưu dangerous hashes vào JSON file
        
        Args:
            json_path: Path to save JSON
        """
        with open(json_path, 'w') as f:
            json.dump(self.dangerous_hashes, f, indent=2)
    
    def get_hash_info(self, file_hash: str) -> dict:
        """
        Lấy thông tin về hash
        
        Args:
            file_hash: File hash
            
        Returns:
            dict với thông tin
        """
        file_hash_lower = file_hash.lower()
        
        if file_hash_lower in self.dangerous_hashes:
            return {
                'status': 'dangerous',
                'hash': file_hash,
                'info': self.dangerous_hashes[file_hash_lower]
            }
        
        elif file_hash_lower in self.whitelist_hashes:
            return {
                'status': 'whitelisted',
                'hash': file_hash
            }
        
        else:
            return {
                'status': 'unknown',
                'hash': file_hash
            }
    
    def verify_file_integrity(self, file_path: str, expected_hash: str) -> bool:
        """
        Xác minh tính toàn vẹn file
        
        Args:
            file_path: Đường dẫn file
            expected_hash: Hash mong đợi
            
        Returns:
            True nếu khớp
        """
        calculated_hash = self.calculate_file_hash(file_path, 'sha256')
        return calculated_hash == expected_hash.lower()


# Ví dụ dangerous hashes database format
SAMPLE_DANGEROUS_HASHES = {
    "f9e4c8a2b1d5e6a7c8b9d0e1f2a3b4c5": {
        "threat_name": "Trojan.PDF.Exploit.Z",
        "threat_category": "Trojan",
        "severity": 9,
        "detected_by": 47,
        "first_seen": "2024-02-15"
    },
    "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6": {
        "threat_name": "Win32.Malware.Generic",
        "threat_category": "Malware",
        "severity": 8,
        "detected_by": 52,
        "first_seen": "2024-01-20"
    }
}
