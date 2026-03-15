"""Test suite for File Security Checker"""

import unittest
import os
import tempfile
from pathlib import Path

# Add src to path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.file_analyzer import FileAnalyzer
from core.hash_manager import HashManager
from core.risk_scorer import RiskScorer


class TestFileAnalyzer(unittest.TestCase):
    """Test FileAnalyzer module"""
    
    def setUp(self):
        self.analyzer = FileAnalyzer()
        # Create temp file for testing
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        # Clean up temp files
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_check_dangerous_extension(self):
        """Test detection of dangerous extensions"""
        analysis = self.analyzer._check_extension('malware.exe')
        self.assertEqual(analysis['status'], 'dangerous')
        self.assertEqual(analysis['risk_score'], 3)
    
    def test_check_safe_extension(self):
        """Test detection of safe extensions"""
        analysis = self.analyzer._check_extension('document.pdf')
        self.assertEqual(analysis['status'], 'safe')
        self.assertEqual(analysis['risk_score'], 0)
    
    def test_check_unknown_extension(self):
        """Test detection of unknown extensions"""
        analysis = self.analyzer._check_extension('file.xyz')
        self.assertEqual(analysis['status'], 'unknown')
        self.assertEqual(analysis['risk_score'], 1)
    
    def test_double_extension_detection(self):
        """Test double extension attack detection"""
        analysis = self.analyzer._check_double_extension('resume.pdf.exe')
        self.assertTrue(analysis['has_double_ext'])
        self.assertEqual(analysis['actual_extension'], 'exe')


class TestHashManager(unittest.TestCase):
    """Test HashManager module"""
    
    def setUp(self):
        self.hash_manager = HashManager()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_calculate_hash(self):
        """Test hash calculation"""
        # Create temp file
        test_file = os.path.join(self.temp_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test content')
        
        file_hash = self.hash_manager.calculate_file_hash(test_file)
        self.assertIsNotNone(file_hash)
        self.assertEqual(len(file_hash), 64)  # SHA256 is 64 hex chars
    
    def test_add_dangerous_hash(self):
        """Test adding dangerous hash"""
        test_hash = 'abc123def456abc123def456abc123de'
        self.hash_manager.add_dangerous_hash(
            test_hash,
            {'threat_name': 'Test.Malware'}
        )
        
        is_dangerous, info = self.hash_manager.is_dangerous_hash(test_hash)
        self.assertTrue(is_dangerous)
    
    def test_whitelist_hash(self):
        """Test whitelist functionality"""
        test_hash = 'abc123def456abc123def456abc123de'
        self.hash_manager.add_whitelist_hash(test_hash)
        self.assertTrue(self.hash_manager.is_whitelisted_hash(test_hash))


class TestRiskScorer(unittest.TestCase):
    """Test RiskScorer module"""
    
    def setUp(self):
        self.scorer = RiskScorer()
    
    def test_get_risk_level_low(self):
        """Test LOW risk level"""
        level = self.scorer.get_risk_level(1.5)
        self.assertEqual(level, 'LOW')
    
    def test_get_risk_level_medium(self):
        """Test MEDIUM risk level"""
        level = self.scorer.get_risk_level(3.0)
        self.assertEqual(level, 'MEDIUM')
    
    def test_get_risk_level_high(self):
        """Test HIGH risk level"""
        level = self.scorer.get_risk_level(5.5)
        self.assertEqual(level, 'HIGH')
    
    def test_get_risk_level_critical(self):
        """Test CRITICAL risk level"""
        level = self.scorer.get_risk_level(8.0)
        self.assertEqual(level, 'CRITICAL')
    
    def test_calculate_score(self):
        """Test score calculation"""
        analysis = {
            'extension': {'risk_score': 0},
            'magic_number': {'risk_score': 0},
            'size': {'risk_score': 0},
            'hash_status': {'risk_score': 0},
            'double_extension': {'has_double_ext': False, 'risk_score': 0}
        }
        
        score, level = self.scorer.calculate_score(analysis)
        self.assertEqual(level, 'LOW')
        self.assertLess(score, 2)


if __name__ == '__main__':
    unittest.main()
