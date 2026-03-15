"""
Database Manager Module
Manage SQLite database operations
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional


class DatabaseManager:
    """Manage SQLite database for scan history and hash database"""
    
    def __init__(self, db_path: str = 'scanner.db'):
        """
        Initialize database manager
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.initialize_database()
    
    def initialize_database(self) -> None:
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Scan history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scan_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_hash VARCHAR(64),
                file_size INTEGER,
                file_extension TEXT,
                magic_number TEXT,
                risk_score REAL,
                risk_level TEXT,
                scan_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_safe BOOLEAN,
                details TEXT
            )
        ''')
        
        # Dangerous hashes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dangerous_hashes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_hash VARCHAR(64) UNIQUE NOT NULL,
                threat_name TEXT,
                threat_category TEXT,
                severity INTEGER,
                added_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Whitelist table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS whitelist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_hash VARCHAR(64) UNIQUE NOT NULL,
                file_name TEXT,
                file_path TEXT,
                added_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                reason TEXT
            )
        ''')
        
        # Custom rules table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS custom_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_name TEXT NOT NULL,
                rule_type TEXT,
                rule_pattern TEXT,
                risk_increment REAL,
                enabled BOOLEAN DEFAULT 1
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_hash ON scan_history(file_hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_risk_level ON scan_history(risk_level)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON scan_history(scan_timestamp)')
        
        conn.commit()
        conn.close()
    
    def save_scan_result(self, scan_result: dict) -> int:
        """
        Lưu kết quả scan vào database
        
        Args:
            scan_result: Dictionary (ví dụ từ RiskScorer.generate_detailed_report)
            
        Returns:
            ID của scan record được tạo
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        file_info = scan_result.get('file_info', {})
        risk_info = scan_result.get('risk_assessment', {})
        
        cursor.execute('''
            INSERT INTO scan_history
            (file_name, file_path, file_hash, file_size, file_extension,
             magic_number, risk_score, risk_level, is_safe, details)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            file_info.get('file_name'),
            file_info.get('file_path'),
            file_info.get('file_hash'),
            file_info.get('file_size'),
            file_info.get('extension'),
            file_info.get('magic_number'),
            risk_info.get('total_score'),
            risk_info.get('level'),
            risk_info.get('level') == 'LOW',
            json.dumps(scan_result)
        ))
        
        conn.commit()
        record_id = cursor.lastrowid
        conn.close()
        
        return record_id
    
    def get_scan_history(self, limit: int = 100) -> List[dict]:
        """
        Lấy lịch sử scan
        
        Args:
            limit: Số lượng records
            
        Returns:
            List of scan records
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM scan_history
            ORDER BY scan_timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return rows
    
    def get_scan_by_hash(self, file_hash: str) -> Optional[dict]:
        """
        Lấy scan result theo hash
        
        Args:
            file_hash: File hash
            
        Returns:
            Scan record or None
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM scan_history
            WHERE file_hash = ?
            ORDER BY scan_timestamp DESC
            LIMIT 1
        ''', (file_hash,))
        
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def add_dangerous_hash(self, file_hash: str, threat_name: str,
                         threat_category: str = None, severity: int = 0) -> None:
        """
        Thêm hash vào dangerous database
        
        Args:
            file_hash: Hash value
            threat_name: Name of threat
            threat_category: Category (Trojan, Virus, etc.)
            severity: Severity level (0-10)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO dangerous_hashes
            (file_hash, threat_name, threat_category, severity)
            VALUES (?, ?, ?, ?)
        ''', (file_hash.lower(), threat_name, threat_category, severity))
        
        conn.commit()
        conn.close()
    
    def get_dangerous_hashes(self) -> dict:
        """
        Lấy tất cả dangerous hashes từ database
        
        Returns:
            Dictionary {hash: threat_info}
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT file_hash, threat_name, threat_category, severity '
                      'FROM dangerous_hashes')
        
        result = {}
        for row in cursor.fetchall():
            result[row[0]] = {
                'threat_name': row[1],
                'threat_category': row[2],
                'severity': row[3]
            }
        
        conn.close()
        return result
    
    def is_whitelisted(self, file_hash: str) -> bool:
        """
        Kiểm tra file có trong whitelist không
        
        Args:
            file_hash: File hash
            
        Returns:
            True nếu whitelisted
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM whitelist WHERE file_hash = ?',
                      (file_hash.lower(),))
        
        result = cursor.fetchone()[0] > 0
        conn.close()
        
        return result
    
    def add_to_whitelist(self, file_hash: str, file_name: str = None,
                        file_path: str = None, reason: str = None) -> None:
        """
        Thêm file vào whitelist
        
        Args:
            file_hash: File hash
            file_name: File name (optional)
            file_path: File path (optional)
            reason: Reason for whitelisting (optional)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO whitelist
            (file_hash, file_name, file_path, reason)
            VALUES (?, ?, ?, ?)
        ''', (file_hash.lower(), file_name, file_path, reason))
        
        conn.commit()
        conn.close()
    
    def get_statistics(self) -> dict:
        """
        Lấy thống kê từ database
        
        Returns:
            Dictionary với statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total scans
        cursor.execute('SELECT COUNT(*) FROM scan_history')
        total_scans = cursor.fetchone()[0]
        
        # Safe files
        cursor.execute('SELECT COUNT(*) FROM scan_history WHERE risk_level = "LOW"')
        safe_count = cursor.fetchone()[0]
        
        # Dangerous files
        cursor.execute('SELECT COUNT(*) FROM scan_history WHERE risk_level IN ("HIGH", "CRITICAL")')
        dangerous_count = cursor.fetchone()[0]
        
        # Dangerous hashes in DB
        cursor.execute('SELECT COUNT(*) FROM dangerous_hashes')
        malware_db = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_scans': total_scans,
            'safe_files': safe_count,
            'dangerous_files': dangerous_count,
            'malware_db_entries': malware_db,
            'safe_percentage': (safe_count / total_scans * 100) if total_scans > 0 else 0
        }
    
    def clear_old_history(self, days: int = 30) -> int:
        """
        Xóa history cũ hơn N days
        
        Args:
            days: Number of days
            
        Returns:
            Number of records deleted
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM scan_history
            WHERE datetime(scan_timestamp) < datetime('now', '-' || ? || ' days')
        ''', (days,))
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted_count
