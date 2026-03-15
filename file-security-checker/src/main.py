"""Main application entry point"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.file_analyzer import FileAnalyzer
from core.hash_manager import HashManager
from core.risk_scorer import RiskScorer
from database.db_manager import DatabaseManager
from utils.config import Config
from utils.logger import setup_logger


class FileSecurityChecker:
    """Main application class"""
    
    def __init__(self, config_path: str = 'config.json'):
        """
        Initialize application
        
        Args:
            config_path: Path to configuration file
        """
        self.config = Config(config_path)
        self.config.ensure_directories()
        
        self.logger = setup_logger(
            self.config.get('log_directory'),
            'file_security_checker'
        )
        
        self.logger.info('Initializing File Security Checker...')
        
        # Initialize components
        self.file_analyzer = FileAnalyzer()
        self.hash_manager = HashManager(
            self.config.get('malware_db_path')
        )
        self.risk_scorer = RiskScorer()
        self.db_manager = DatabaseManager(
            self.config.get('database_path')
        )
        
        self.logger.info('Application initialized successfully')
    
    def scan_file(self, file_path: str) -> dict:
        """
        Scan a file for security threats
        
        Args:
            file_path: Path to file to scan
            
        Returns:
            Complete scan report
        """
        self.logger.info(f'Starting scan: {file_path}')
        
        try:
            # Step 1: File analysis
            analysis = self.file_analyzer.analyze_file(file_path)
            
            if 'error' in analysis:
                self.logger.error(f'File analysis error: {analysis["error"]}')
                return {'error': analysis['error']}
            
            # Step 2: Calculate hash
            try:
                file_hash = self.hash_manager.calculate_file_hash(file_path)
                analysis['file_info']['file_hash'] = file_hash
            except Exception as e:
                self.logger.warning(f'Hash calculation failed: {e}')
                file_hash = None
            
            # Step 3: Check hash status
            if file_hash:
                is_whitelisted = self.hash_manager.is_whitelisted_hash(file_hash)
                is_dangerous, threat_info = self.hash_manager.is_dangerous_hash(file_hash)
                
                if is_whitelisted:
                    analysis['hash_status'] = {
                        'status': 'whitelisted',
                        'hash': file_hash,
                        'risk_score': 0
                    }
                elif is_dangerous:
                    analysis['hash_status'] = {
                        'status': 'dangerous',
                        'hash': file_hash,
                        'risk_score': 3,
                        'threat_name': threat_info.get('threat_name', 'Unknown'),
                        'threat_category': threat_info.get('threat_category')
                    }
                else:
                    analysis['hash_status'] = {
                        'status': 'unknown',
                        'hash': file_hash,
                        'risk_score': 1
                    }
            
            # Step 4: Calculate risk score
            risk_score, risk_level = self.risk_scorer.calculate_score(analysis)
            
            # Step 5: Generate detailed report
            report = self.risk_scorer.generate_detailed_report(file_path, analysis)
            
            # Step 6: Save to database
            try:
                self.db_manager.save_scan_result(report)
                self.logger.info(f'Scan saved to database: {risk_level}')
            except Exception as e:
                self.logger.error(f'Database save error: {e}')
            
            self.logger.info(f'Scan completed: {file_path} - Risk: {risk_level}')
            
            return report
        
        except Exception as e:
            self.logger.error(f'Scan error: {e}', exc_info=True)
            return {'error': str(e)}
    
    def get_scan_history(self, limit: int = 50) -> list:
        """Get recent scan history"""
        return self.db_manager.get_scan_history(limit)
    
    def get_statistics(self) -> dict:
        """Get application statistics"""
        return self.db_manager.get_statistics()
    
    def whitelist_file(self, file_hash: str, file_name: str = None) -> None:
        """Add file to whitelist"""
        self.hash_manager.add_whitelist_hash(file_hash)
        self.db_manager.add_to_whitelist(file_hash, file_name)
        self.logger.info(f'File whitelisted: {file_hash}')


def main():
    """Main CLI interface"""
    if len(sys.argv) < 2:
        print('Máy Quét Bảo Mật Tập Tin CLI')
        print('Cách dùng: python main.py <đường_dẫn_tập_tin>')
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    # Initialize application
    app = FileSecurityChecker()
    
    # Scan file
    report = app.scan_file(file_path)
    
    # Print results
    if 'error' in report:
        print(f'Lỗi: {report["error"]}')
    else:
        print('\n' + '='*60)
        print('BÁO CÁO QUÉT BẢO MẬT TẬP TIN')
        print('='*60)
        
        file_info = report.get('file_info', {})
        risk_info = report.get('risk_assessment', {})
        
        print(f'Tập tin: {file_info.get("file_name")}')
        print(f'Kích thước: {file_info.get("file_size_kb")} KB')
        print(f'Mã hash: {file_info.get("file_hash", "Không có")[:16]}...')
        
        print(f'\nĐiểm rủi ro: {risk_info.get("total_score")}/10 - {risk_info.get("level")}')
        
        print('\nLý do:')
        for reason in risk_info.get('reasons', []):
            print(f'  {reason}')
        
        print(f'\nKhuyến nghị:')
        print(f'  {report.get("recommendation", "Không có")}')
        
        print('='*60)


if __name__ == '__main__':
    main()
