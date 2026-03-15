"""
File Analyzer Module
Analyze file extension, magic number, size, and metadata
"""

import os
import json
from pathlib import Path
from datetime import datetime
from .magic_numbers import MAGIC_NUMBERS, detect_file_type


# Dangerous & Safe Extensions Database
DANGEROUS_EXTENSIONS = {
    'exe', 'dll', 'com', 'scr', 'vbs', 'js', 'jse',
    'bat', 'cmd', 'ps1', 'psc1', 'msh', 'msh1', 'msh2', 'mshxml',
    'msh1xml', 'msh2xml', 'sh', 'app', 'msi', 'psz', 'mst', 'ocx',
    'cpl', 'hta', 'sct', 'zip', 'rar', 'iso', 'cab', 'zip',
    'scr', 'pif', 'vbs', 'js', 'action', 'apk', 'deb', 'pkg'
}

SAFE_EXTENSIONS = {
    'txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
    'jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'tiff', 'webp',
    'mp3', 'mp4', 'mov', 'avi', 'mkv', 'flv', 'wav', 'flac',
    'csv', 'json', 'xml', 'html', 'htm', 'css', 'log', 'md'
}


class FileAnalyzer:
    """Analyze file characteristics for security assessment"""
    
    def __init__(self):
        self.dangerous_exts = DANGEROUS_EXTENSIONS
        self.safe_exts = SAFE_EXTENSIONS
    
    def analyze_file(self, file_path: str) -> dict:
        """
        Phân tích toàn bộ file
        
        Args:
            file_path: Đường dẫn file
            
        Returns:
            dict chứa kết quả phân tích
        """
        try:
            # Check file exists
            if not os.path.exists(file_path):
                return {'error': f'File not found: {file_path}'}
            
            result = {
                'file_info': self._get_file_info(file_path),
                'extension': self._check_extension(file_path),
                'magic_number': self._check_magic_number(file_path),
                'size': self._analyze_size(file_path),
                'metadata': self._get_metadata(file_path),
                'double_extension': self._check_double_extension(file_path)
            }
            
            return result
        
        except Exception as e:
            return {'error': str(e)}
    
    def _get_file_info(self, file_path: str) -> dict:
        """Lấy thông tin cơ bản về file"""
        stat = os.stat(file_path)
        
        return {
            'file_name': os.path.basename(file_path),
            'file_path': file_path,
            'absolute_path': os.path.abspath(file_path),
            'file_size': stat.st_size,
            'file_size_kb': round(stat.st_size / 1024, 2),
            'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'accessed_time': datetime.fromtimestamp(stat.st_atime).isoformat()
        }
    
    def _check_extension(self, file_path: str) -> dict:
        """Kiểm tra extension của file"""
        _, ext = os.path.splitext(file_path)
        ext = ext.lstrip('.').lower()
        
        if not ext:
            return {
                'extension': 'NO_EXTENSION',
                'status': 'unknown',
                'risk_score': 1,
                'reason': 'File has no extension'
            }
        
        if ext in self.dangerous_exts:
            return {
                'extension': ext,
                'status': 'dangerous',
                'risk_score': 3,
                'reason': f'{ext.upper()} is a dangerous executable extension'
            }
        
        elif ext in self.safe_exts:
            return {
                'extension': ext,
                'status': 'safe',
                'risk_score': 0,
                'reason': f'{ext.upper()} is generally safe'
            }
        
        else:
            return {
                'extension': ext,
                'status': 'unknown',
                'risk_score': 1,
                'reason': f'{ext.upper()} is unknown'
            }
    
    def _check_magic_number(self, file_path: str) -> dict:
        """Kiểm tra magic number (file signature)"""
        try:
            with open(file_path, 'rb') as f:
                file_header = f.read(32)
            
            if not file_header:
                return {
                    'error': 'Empty file',
                    'risk_score': 1
                }
            
            # Check magic numbers
            for magic_sig, (file_type, expected_exts) in MAGIC_NUMBERS.items():
                if file_header.startswith(magic_sig):
                    _, actual_ext = os.path.splitext(file_path)
                    actual_ext = actual_ext.lstrip('.').lower()
                    
                    if actual_ext in expected_exts:
                        return {
                            'magic_detected': magic_sig.hex(),
                            'file_type': file_type,
                            'expected_extensions': list(expected_exts),
                            'actual_extension': actual_ext,
                            'match': True,
                            'risk_score': 0,
                            'status': 'match'
                        }
                    else:
                        return {
                            'magic_detected': magic_sig.hex(),
                            'file_type': file_type,
                            'expected_extensions': list(expected_exts),
                            'actual_extension': actual_ext,
                            'match': False,
                            'risk_score': 2,
                            'status': 'mismatch',
                            'warning': f'Extension mismatch! File signature indicates {expected_exts}'
                        }
            
            # Unknown magic number
            return {
                'magic_detected': file_header[:8].hex(),
                'match': None,
                'risk_score': 1,
                'status': 'unknown',
                'warning': 'Unknown file signature'
            }
        
        except Exception as e:
            return {
                'error': str(e),
                'risk_score': 1
            }
    
    def _analyze_size(self, file_path: str) -> dict:
        """Phân tích kích thước file bất thường"""
        file_size = os.path.getsize(file_path)
        
        # Thresholds (in bytes)
        NORMAL_MIN = 1  # At least 1 byte
        NORMAL_MAX = 100 * 1024 * 1024  # 100 MB
        SUSPICIOUS_THRESHOLD = 500 * 1024 * 1024  # 500 MB
        
        if file_size < NORMAL_MIN:
            return {
                'size': file_size,
                'status': 'suspicious',
                'risk_score': 1,
                'reason': 'File is empty or very small'
            }
        
        elif file_size > SUSPICIOUS_THRESHOLD:
            return {
                'size': file_size,
                'size_mb': round(file_size / (1024 * 1024), 2),
                'status': 'anomalous',
                'risk_score': 2,
                'reason': f'File is unusually large: {round(file_size / (1024*1024), 1)} MB'
            }
        
        elif file_size <= NORMAL_MAX:
            return {
                'size': file_size,
                'size_kb': round(file_size / 1024, 2),
                'status': 'normal',
                'risk_score': 0,
                'reason': 'File size is normal'
            }
        
        return {
            'size': file_size,
            'status': 'unknown',
            'risk_score': 0
        }
    
    def _get_metadata(self, file_path: str) -> dict:
        """Lấy metadata file"""
        path = Path(file_path)
        
        return {
            'is_readable': os.access(file_path, os.R_OK),
            'is_writeable': os.access(file_path, os.W_OK),
            'is_executable': os.access(file_path, os.X_OK),
            'is_symlink': os.path.islink(file_path),
            'permissions': oct(os.stat(file_path).st_mode)[-3:],
            'owner_uid': os.stat(file_path).st_uid if hasattr(os, 'stat') else 'N/A'
        }
    
    def _check_double_extension(self, file_path: str) -> dict:
        """Kiểm tra double extension attack (e.g., file.txt.exe)"""
        file_name = os.path.basename(file_path)
        parts = file_name.rsplit('.', 2)
        
        if len(parts) == 3:
            visible_ext = parts[1].lower()
            actual_ext = parts[2].lower()
            
            if actual_ext in self.dangerous_exts:
                return {
                    'has_double_ext': True,
                    'visible_extension': visible_ext,
                    'actual_extension': actual_ext,
                    'risk_score': 3,
                    'status': 'critical',
                    'reason': f'Double extension attack detected! '
                             f'Appears as .{visible_ext} but actually .{actual_ext}'
                }
        
        return {
            'has_double_ext': False,
            'risk_score': 0
        }
