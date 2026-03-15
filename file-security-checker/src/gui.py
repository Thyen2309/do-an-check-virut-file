"""GUI Module for File Security Checker"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import json
from datetime import datetime
from main import FileSecurityChecker


class FileSecurityCheckerGUI:
    """GUI application using Tkinter"""
    
    def __init__(self, root: tk.Tk):
        """Initialize GUI"""
        self.root = root
        self.root.title('Máy Quét Bảo Mật Tập Tin')
        self.root.geometry('800x600')
        
        # Initialize app logic
        self.app = FileSecurityChecker()
        
        # Setup GUI
        self.setup_gui()
    
    def setup_gui(self):
        """Setup GUI components"""
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding='10')
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text='Máy Quét Bảo Mật Tập Tin',
            font=('Arial', 16, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # File selection section
        file_frame = ttk.LabelFrame(main_frame, text='Chọn Tập Tin', padding='10')
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=50)
        file_entry.grid(row=0, column=0, padx=5)
        
        browse_btn = ttk.Button(
            file_frame,
            text='Duyệt',
            command=self.browse_file
        )
        browse_btn.grid(row=0, column=1, padx=5)
        
        # Scan button
        scan_btn = ttk.Button(
            main_frame,
            text='Quét Tập Tin',
            command=self.scan_file
        )
        scan_btn.grid(row=2, column=0, columnspan=3, pady=10)
        
        # Results section
        results_frame = ttk.LabelFrame(main_frame, text='Kết Quả Quét', padding='10')
        results_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.results_text = tk.Text(results_frame, height=20, width=80)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.results_text.config(yscrollcommand=scrollbar.set)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def browse_file(self):
        """Open file browser dialog"""
        file_path = filedialog.askopenfilename(
            title='Chọn tập tin cần quét',
            filetypes=[('Tất cả các tập tin', '*.*')]
        )
        
        if file_path:
            self.file_path_var.set(file_path)
    
    def scan_file(self):
        """Scan selected file"""
        file_path = self.file_path_var.get()
        
        if not file_path:
            messagebox.showerror('Lỗi', 'Vui lòng chọn một tập tin')
            return
        
        # Disable scan button
        self.root.after(0, self._perform_scan, file_path)
    
    def _perform_scan(self, file_path):
        """Perform scan (in GUI thread)"""
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, 'Đang quét...\n')
        self.root.update()
        
        try:
            report = self.app.scan_file(file_path)
            self.display_results(report)
        except Exception as e:
            self.results_text.insert(tk.END, f'Lỗi: {str(e)}')
    
    def display_results(self, report: dict):
        """Display scan results in text widget"""
        self.results_text.delete(1.0, tk.END)
        
        if 'error' in report:
            self.results_text.insert(tk.END, f'Lỗi: {report["error"]}\n')
            return
        
        # Format results
        file_info = report.get('file_info', {})
        risk_info = report.get('risk_assessment', {})
        
        output = []
        output.append('='*70)
        output.append('BÁO CÁO QUÉT BẢO MẬT TẬP TIN')
        output.append('='*70)
        output.append('')
        
        output.append(f'Đường dẫn: {file_info.get("file_path")}')
        output.append(f'Tên tập tin: {file_info.get("file_name")}')
        output.append(f'Kích thước: {file_info.get("file_size_kb")} KB')
        output.append(f'Phần mở rộng: {file_info.get("file_extension")}')
        output.append(f'Mã hash: {file_info.get("file_hash", "Không có")[:48]}...')
        output.append(f'Thời gian quét: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        
        output.append('')
        output.append('ĐÁNH GIÁ RỦI RO')
        output.append('-'*70)
        output.append(f'Điểm rủi ro: {risk_info.get("total_score")}/10')
        output.append(f'Mức độ rủi ro: {risk_info.get("level")}')
        
        output.append('')
        output.append('KắT QUẢ PHÂN TÍCH')
        output.append('-'*70)
        
        analysis = report.get('analysis_results', {})
        for key, value in analysis.items():
            if isinstance(value, dict) and value:
                output.append(f'{key.upper()}:')
                for k, v in value.items():
                    output.append(f'  {k}: {v}')
        
        output.append('')
        output.append('LÝ DO CỦA ĐIỂM RỦI RO')
        output.append('-'*70)
        for reason in risk_info.get('reasons', []):
            output.append(f'  • {reason}')
        
        output.append('')
        output.append('KHUYẪ NGHị')
        output.append('-'*70)
        output.append(report.get('recommendation', 'Không có'))
        
        output.append('')
        output.append('HÀNH ĐỘNGĐƯợC KHUYẪ NGHị')
        output.append('-'*70)
        for action in report.get('action_items', []):
            output.append(f'  • {action}')
        
        output.append('='*70)
        
        self.results_text.insert(tk.END, '\n'.join(output))


def main():
    """Main GUI entry point"""
    root = tk.Tk()
    gui = FileSecurityCheckerGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
