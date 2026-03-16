"""
Risk Scorer Module
Calculate risk score based on multiple factors
"""


class RiskScorer:
    """Calculate security risk score for files"""
    
    # Weights for different factors (total = 1.0)
    WEIGHTS = {
        'extension': 0.25,
        'magic_number': 0.20,
        'hash': 0.35,
        'size': 0.10,
        'metadata': 0.10,
        'behavioral': 0.30
    }
    
    # Risk level thresholds
    RISK_LEVELS = {
        'LOW': (0, 2),
        'MEDIUM': (2, 4),
        'HIGH': (4, 7),
        'CRITICAL': (7, 10)
    }
    
    def calculate_score(self, analysis: dict) -> tuple:
        """
        Tính tổng risk score
        
        Args:
            analysis: Dictionary từ FileAnalyzer
            
        Returns:
            (score, risk_level) tuple
        """
        if 'error' in analysis:
            return 5.0, 'MEDIUM'  # Default medium risk if error
        
        score = 0.0
        
        # Extension risk
        ext_info = analysis.get('extension', {})
        ext_risk = ext_info.get('risk_score', 0)
        score += ext_risk * self.WEIGHTS['extension']
        
        # Magic number risk
        magic_info = analysis.get('magic_number', {})
        magic_risk = magic_info.get('risk_score', 0)
        score += magic_risk * self.WEIGHTS['magic_number']
        
        # Hash risk (will be filled by hash_manager)
        hash_info = analysis.get('hash_status', {})
        hash_risk = hash_info.get('risk_score', 0)
        score += hash_risk * self.WEIGHTS['hash']
        
        # Size risk
        size_info = analysis.get('size', {})
        size_risk = size_info.get('risk_score', 0)
        score += size_risk * self.WEIGHTS['size']
        
        # Double extension risk
        double_ext = analysis.get('double_extension', {})
        if double_ext.get('has_double_ext'):
            score += double_ext.get('risk_score', 0) * 0.15  # Additional penalty
        
        # Behavioral risk (only when executable behavior analysis exists)
        behavioral_info = analysis.get('behavioral', {})
        behavioral_risk = behavioral_info.get('risk_score', 0)
        score += behavioral_risk * self.WEIGHTS['behavioral']

        # Cap score at 10
        final_score = min(round(score, 2), 10.0)
        risk_level = self.get_risk_level(final_score)
        
        return final_score, risk_level
    
    def get_risk_level(self, score: float) -> str:
        """
        Xác định mức độ risk từ score
        
        Args:
            score: Risk score (0-10)
            
        Returns:
            Risk level string
        """
        for level, (min_score, max_score) in self.RISK_LEVELS.items():
            if min_score <= score < max_score:
                return level
        
        return 'CRITICAL'
    
    def get_risk_icon(self, risk_level: str) -> str:
        """
        Lấy icon/emoji cho risk level
        
        Args:
            risk_level: Risk level string
            
        Returns:
            Icon string
        """
        icons = {
            'LOW': '✓',
            'MEDIUM': '⚠',
            'HIGH': '⛔',
            'CRITICAL': '🔴'
        }
        return icons.get(risk_level, '?')
    
    def get_risk_color(self, risk_level: str) -> str:
        """
        Lấy màu cho risk level (for GUI)
        
        Args:
            risk_level: Risk level string
            
        Returns:
            Color code
        """
        colors = {
            'LOW': 'green',
            'MEDIUM': 'orange',
            'HIGH': 'red',
            'CRITICAL': 'darkred'
        }
        return colors.get(risk_level, 'gray')
    
    def generate_reasons(self, analysis: dict) -> list:
        """
        Tạo danh sách lý do chiếm cao risk
        
        Args:
            analysis: Analysis result
            
        Returns:
            List of reason strings
        """
        reasons = []
        
        # Extension reason
        ext_info = analysis.get('extension', {})
        if ext_info.get('status') == 'dangerous':
            reasons.append(f"⚠ Phần mở rộng nguy hiểm: .{ext_info.get('extension')}")
        elif ext_info.get('status') == 'unknown':
            reasons.append(f"⚠ Phần mở rộng chưa biết: .{ext_info.get('extension')}")
        
        # Magic number reason
        magic_info = analysis.get('magic_number', {})
        if magic_info.get('match') == False:
            reasons.append("⚠ Mã file không khớp: Chữ ký tập tin không mặn extension")
            if 'warning' in magic_info:
                reasons.append(f"   → {magic_info.get('warning')}")
        
        # Hash reason
        hash_info = analysis.get('hash_status', {})
        if hash_info.get('status') == 'dangerous':
            threat_name = hash_info.get('threat_name', 'Mối đe dọa')
            reasons.append(f"🔴 PHÁT HIỆN MALWARE: {threat_name}")
        elif hash_info.get('status') == 'unknown':
            reasons.append("⚠ Mã hash tập tin không có trong cơ sở dữ liệu đáng tin cậy (tập tin chưa biết)")
        
        # Size reason
        size_info = analysis.get('size', {})
        if size_info.get('status') == 'anomalous':
            reasons.append(f"⚠ Kích thước tập tin bất thường: {size_info.get('size_mb', 'Không có')} MB")
        elif size_info.get('status') == 'suspicious':
            reasons.append("⚠ Tập tin rất nhỏ hoặc trống")
        
        # Double extension reason
        double_ext = analysis.get('double_extension', {})
        if double_ext.get('has_double_ext'):
            visible = double_ext.get('visible_extension')
            actual = double_ext.get('actual_extension')
            reasons.append(f"🔴 CRỊTICAL: Nhập hiệu phần mở rộng kép (.{visible}.{actual})")
            reasons.append(f"   → Cuộc tấn công giả mạo! Nhìn như .{visible} nhưng thực tế .{actual}")
        
        # Behavioral analysis reasons
        behavioral = analysis.get('behavioral', {})
        if behavioral.get('is_pe'):
            if behavioral.get('has_dangerous_apis'):
                reasons.append(
                    f"⚠ Behavioral: phát hiện {behavioral.get('dangerous_api_count', 0)} API nguy hiểm"
                )
            if behavioral.get('is_packed'):
                pack_types = ', '.join(behavioral.get('packing_types', [])) or 'unknown'
                reasons.append(f"⚠ Behavioral: file có dấu hiệu bị pack/encrypt ({pack_types})")

        return reasons
    
    def get_recommendation(self, risk_level: str, analysis: dict = None) -> str:
        """
        Đưa ra kh uyến nghị dựa trên risk level
        
        Args:
            risk_level: Risk level
            analysis: Analysis result (optional, for detailed recommendations)
            
        Returns:
            Recommendation string
        """
        if risk_level == 'LOW':
            return "✓ Tập tin này có vẻ an toàn. Bạn có thể mở nó với tín in."
        
        elif risk_level == 'MEDIUM':
            return "⚠ Tập tin này có những đặc điểm đáng ngỊ ng. " \
                   "Hãy cẩn thận và xác thực nguồn trước khi mở."
        
        elif risk_level == 'HIGH':
            return "⚠ Tập tin này đáng ngỊ ng. \u0110ùng mở nó.\n" \
                   "Cân nhắc cach ly hoặc xóa nó."
        
        elif risk_level == 'CRITICAL':
            return "🔴 CHỚA Tập tin này rất đáng ngỊ ng hoặc là malware đã biết.\n" \
                   "ĐÙNG Mở NÓ! Hàng động ngằm lập được khuyến nghị:\n" \
                   "• Cach ly tập tin\n" \
                   "• Báo cáo cho nhà cung cấp antivirus\n" \
                   "• Kiểm tra hệ thống xem có nhiễm bệnh không"
        
        return "Mức rủi ro chưa biết"
    
    def generate_detailed_report(self, file_path: str, analysis: dict) -> dict:
        """
        Generate detailed security report
        
        Args:
            file_path: Original file path
            analysis: Complete analysis result
            
        Returns:
            Detailed report dictionary
        """
        score, risk_level = self.calculate_score(analysis)
        reasons = self.generate_reasons(analysis)
        recommendation = self.get_recommendation(risk_level, analysis)
        
        report = {
            'file_info': analysis.get('file_info', {}),
            'analysis_results': {
                'extension': analysis.get('extension', {}),
                'magic_number': analysis.get('magic_number', {}),
                'size': analysis.get('size', {}),
                'hash_status': analysis.get('hash_status', {}),
                'double_extension': analysis.get('double_extension', {}),
                'behavioral': analysis.get('behavioral', {})
            },
            'risk_assessment': {
                'total_score': score,
                'level': risk_level,
                'icon': self.get_risk_icon(risk_level),
                'color': self.get_risk_color(risk_level),
                'reasons': reasons
            },
            'recommendation': recommendation,
            'action_items': self._get_action_items(risk_level, analysis)
        }
        
        return report
    
    def _get_action_items(self, risk_level: str, analysis: dict) -> list:
        """
        Lấy các hàng động khuyến nghị dựa trên risk level
        
        Args:
            risk_level: Risk level
            analysis: Analysis result
            
        Returns:
            List of action items
        """
        actions = []
        
        if risk_level == 'LOW':
            actions.append('✓ An toàn để mở')
        
        elif risk_level == 'MEDIUM':
            actions.append('⚠ Xác thực nguồn trước khi mở')
            actions.append('💾 Giữu lại bản sao trước khi mở')
        
        elif risk_level == 'HIGH':
            actions.append('⚠ Đùng mở')
            actions.append('🗘 Cân nhắc xóa')
        
        elif risk_level == 'CRITICAL':
            actions.append('🔴 Cách ly ngay lắc')
            actions.append('🗘 Xóa tập tin')
            actions.append('🛡 Quét hệ thống để check nhiễm bệnh')
            actions.append('📮 Báo cáo cho người gửi')
        
        return actions
