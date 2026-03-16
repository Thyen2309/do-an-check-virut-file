"""
Behavioral Analysis Module
Analyze PE executable behavior and characteristics for malware detection
"""

import struct
import math
from typing import Dict, List, Tuple


class BehavioralAnalyzer:
    """Analyze file behavior characteristics"""
    
    # Dangerous APIs commonly used by malware
    DANGEROUS_APIS = {
        # Process manipulation
        'CreateRemoteThread': 9,
        'WriteProcessMemory': 9,
        'VirtualAllocEx': 8,
        'GetWindowTextA': 7,
        'GetWindowTextW': 7,
        'SetWindowsHookEx': 9,
        
        # Registry/System
        'RegOpenKeyEx': 6,
        'RegSetValueEx': 7,
        'RegDeleteKey': 8,
        'RegQueryValueEx': 6,
        
        # File operations
        'CreateFileA': 5,
        'CreateFileW': 5,
        'DeleteFileA': 7,
        'DeleteFileW': 7,
        
        # Network
        'InternetOpenA': 6,
        'InternetOpenW': 6,
        'InternetOpenUrlA': 7,
        'InternetOpenUrlW': 7,
        'WSASocket': 6,
        'connect': 6,
        
        # DLL injection
        'LoadLibraryA': 6,
        'LoadLibraryW': 6,
        'GetProcAddress': 7,
        
        # Shell operations
        'ShellExecuteA': 8,
        'ShellExecuteW': 8,
        'WinExec': 8,
        'CreateProcessA': 7,
        'CreateProcessW': 7,
    }
    
    # Known packing signatures
    PACKING_SIGNATURES = {
        'UPX': b'UPX',
        'ASPack': b'ASPack',
        'PECompact': b'PEC',
        'Themida': b'Themida',
        'VMProtect': b'VMProtect',
        '.packed': b'.packed',
        '.UPX': b'.UPX',
    }
    
    def __init__(self):
        pass
    
    def analyze_pe_file(self, file_path: str) -> Dict:
        """
        Analyze PE executable file for malicious behavior
        
        Args:
            file_path: Path to PE file
            
        Returns:
            Dictionary with behavior analysis results
        """
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read(8192)  # Read first 8KB for analysis
            
            if len(file_data) < 2:
                return {'error': 'File too small', 'risk_score': 0}
            
            # Check if PE file
            if not self._is_pe_file(file_data):
                return {
                    'is_pe': False,
                    'risk_score': 0,
                    'behavior_type': 'non-executable'
                }
            
            # PE file analysis
            pe_analysis = {
                'is_pe': True,
                'has_dangerous_apis': False,
                'dangerous_api_count': 0,
                'dangerous_apis': [],
                'is_packed': False,
                'packing_type': None,
                'entropy_score': self._calculate_entropy(file_data),
                'entropy_status': 'normal'
            }
            
            # Check for dangerous APIs in import table
            api_info = self._check_dangerous_apis(file_data)
            pe_analysis.update(api_info)
            
            # Check for packing signatures
            packing_info = self._detect_packing(file_data)
            pe_analysis.update(packing_info)
            
            # Calculate risk score
            risk_score = self._calculate_behavior_risk(pe_analysis)
            pe_analysis['risk_score'] = risk_score
            pe_analysis['behavior_verdict'] = self._get_behavior_verdict(risk_score)
            
            return pe_analysis
            
        except Exception as e:
            return {'error': str(e), 'risk_score': 0}
    
    def _is_pe_file(self, file_data: bytes) -> bool:
        """Check if file is PE executable"""
        # Check MZ header
        if len(file_data) < 2 or file_data[:2] != b'MZ':
            return False
        
        # Check PE signature (0x3C offset points to PE header)
        if len(file_data) >= 0x40:
            pe_offset_addr = 0x3C
            if len(file_data) > pe_offset_addr + 4:
                try:
                    pe_offset = struct.unpack('<I', file_data[pe_offset_addr:pe_offset_addr+4])[0]
                    if pe_offset < len(file_data) - 4:
                        if file_data[pe_offset:pe_offset+2] == b'PE':
                            return True
                except:
                    pass
        
        return False
    
    def _check_dangerous_apis(self, file_data: bytes) -> Dict:
        """Check for dangerous APIs in import table"""
        dangerous_found = []
        total_risk = 0
        
        for api_name, risk_level in self.DANGEROUS_APIS.items():
            # Search for API names in file (simple string matching)
            api_bytes = api_name.encode('ascii') + b'\x00'
            if api_bytes in file_data:
                dangerous_found.append({
                    'api': api_name,
                    'risk_level': risk_level
                })
                total_risk += risk_level
        
        return {
            'has_dangerous_apis': len(dangerous_found) > 0,
            'dangerous_api_count': len(dangerous_found),
            'dangerous_apis': dangerous_found,
            'api_risk_score': min(total_risk / 10, 8)  # Cap at 8
        }
    
    def _detect_packing(self, file_data: bytes) -> Dict:
        """Detect packing/encryption signatures"""
        packing_detected = []
        is_packed = False
        
        for pack_name, pack_sig in self.PACKING_SIGNATURES.items():
            if pack_sig in file_data:
                packing_detected.append(pack_name)
                is_packed = True
        
        # High entropy also indicates packing/encryption
        entropy = self._calculate_entropy(file_data)
        entropy_status = 'normal'
        if entropy > 7.5:
            entropy_status = 'suspicious'
            if not is_packed:
                is_packed = True
                packing_detected.append('Encrypted/High Entropy')
        
        return {
            'is_packed': is_packed,
            'packing_types': packing_detected,
            'entropy_score': entropy,
            'entropy_status': entropy_status,
            'packing_risk_score': 5 if is_packed else 0
        }
    
    def _calculate_entropy(self, data: bytes) -> float:
        """
        Calculate Shannon entropy of file
        High entropy (>7.5) suggests encryption/packing
        
        Args:
            data: File data
            
        Returns:
            Entropy value (0-8)
        """
        if len(data) == 0:
            return 0
        
        # Count byte frequencies
        byte_counts = [0] * 256
        for byte in data:
            byte_counts[byte] += 1
        
        # Calculate entropy
        entropy = 0.0
        data_len = len(data)
        
        for count in byte_counts:
            if count > 0:
                probability = count / data_len
                entropy -= probability * math.log2(probability)
        
        return round(entropy, 2)
    
    def _calculate_behavior_risk(self, analysis: Dict) -> float:
        """
        Calculate overall behavior risk score
        
        Args:
            analysis: Behavior analysis result
            
        Returns:
            Risk score (0-10)
        """
        risk = 0.0
        
        # API risk (max 5 points)
        if analysis.get('has_dangerous_apis'):
            api_count = analysis.get('dangerous_api_count', 0)
            risk += min(api_count * 1.5, 5)
        
        # Packing risk (max 4 points)
        if analysis.get('is_packed'):
            risk += 4
        
        # Entropy risk (max 3 points)
        entropy = analysis.get('entropy_score', 0)
        if entropy > 7.5:
            risk += 3
        elif entropy > 7.0:
            risk += 2
        
        return min(round(risk, 1), 10)
    
    def _get_behavior_verdict(self, risk_score: float) -> str:
        """Get human-readable verdict based on behavior risk"""
        if risk_score >= 7:
            return 'Rất nghi ngờ (Likely Malware)'
        elif risk_score >= 5:
            return 'Nghi ngờ (Suspicious)'
        elif risk_score >= 3:
            return 'Cảnh báo (Caution)'
        else:
            return 'Bình thường (Normal)'


def analyze_file_behavior(file_path: str) -> Dict:
    """
    Convenience function to analyze file behavior
    
    Args:
        file_path: Path to file
        
    Returns:
        Behavior analysis result
    """
    analyzer = BehavioralAnalyzer()
    return analyzer.analyze_pe_file(file_path)
