"""GUI Module for File Security Checker"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import json
from datetime import datetime
from main import FileSecurityChecker


def translate_risk_level(level: str) -> str:
    """Dịch risk level sang tiếng Việt"""
    translation = {
        'LOW': 'Thấp',
        'MEDIUM': 'Trung bình',
        'HIGH': 'Cao',
        'CRITICAL': 'Tới hạn'
    }
    return translation.get(level, level)


class FileSecurityCheckerGUI:
    """GUI application using Tkinter"""
    
    def __init__(self, root: tk.Tk):
        """Initialize GUI"""
        self.root = root
        self.root.title('Máy Quét Bảo Mật Tập Tin')
        self.root.geometry('1000x700')
        
        # Initialize app logic
        self.app = FileSecurityChecker()
        
        # Setup GUI
        self.setup_gui()
    
    def setup_gui(self):
        """Setup GUI components with tabs"""
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding='10')
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text='Máy Quét Bảo Mật Tập Tin',
            font=('Arial', 16, 'bold')
        )
        title_label.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=10)
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Tab 1: Scan
        self.setup_scan_tab()
        
        # Tab 2: History
        self.setup_history_tab()
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
    
    def setup_scan_tab(self):
        """Setup scan tab"""
        scan_frame = ttk.Frame(self.notebook)
        self.notebook.add(scan_frame, text='Quét Tập Tin')
        
        # File selection section
        file_frame = ttk.LabelFrame(scan_frame, text='Chọn Tập Tin', padding='10')
        file_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), padx=10, pady=10)
        
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
            scan_frame,
            text='Quét Tập Tin',
            command=self.scan_file
        )
        scan_btn.grid(row=1, column=0, columnspan=3, pady=10)
        
        # Results section
        results_frame = ttk.LabelFrame(scan_frame, text='Kết Quả Quét', padding='10')
        results_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        
        self.results_text = tk.Text(results_frame, height=25, width=80)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.results_text.config(yscrollcommand=scrollbar.set)
        
        # Configure grid weights
        scan_frame.columnconfigure(0, weight=1)
        scan_frame.rowconfigure(2, weight=1)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
    
    def setup_history_tab(self):
        """Setup scan history tab"""
        history_frame = ttk.Frame(self.notebook)
        self.notebook.add(history_frame, text='Lịch Sử Quét')
        
        # Control buttons
        control_frame = ttk.Frame(history_frame, padding='10')
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        refresh_btn = ttk.Button(
            control_frame,
            text='Làm Mới',
            command=self.refresh_history
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = ttk.Button(
            control_frame,
            text='Xóa Bản Ghi',
            command=self.delete_history_record
        )
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        # History table
        table_frame = ttk.Frame(history_frame)
        table_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        
        # Columns: Thời gian, Tên tập tin, Đường dẫn, Mức rủi ro, Điểm
        self.history_tree = ttk.Treeview(
            table_frame,
            columns=('Thời gian', 'Tên tập tin', 'Đường dẫn', 'Mức độ', 'Điểm'),
            height=15,
            show='headings'
        )
        
        self.history_tree.column('Thời gian', width=150, anchor='center')
        self.history_tree.column('Tên tập tin', width=150, anchor='w')
        self.history_tree.column('Đường dẫn', width=300, anchor='w')
        self.history_tree.column('Mức độ', width=80, anchor='center')
        self.history_tree.column('Điểm', width=60, anchor='center')
        
        self.history_tree.heading('Thời gian', text='Thời gian')
        self.history_tree.heading('Tên tập tin', text='Tên tập tin')
        self.history_tree.heading('Đường dẫn', text='Đường dẫn')
        self.history_tree.heading('Mức độ', text='Mức độ')
        self.history_tree.heading('Điểm', text='Điểm')
        
        self.history_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.history_tree.bind('<<TreeviewSelect>>', self.on_history_select)
        
        # Scrollbar for tree
        tree_scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        tree_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.history_tree.config(yscrollcommand=tree_scroll.set)
        
        # Detail panel
        detail_frame = ttk.LabelFrame(history_frame, text='Chi Tiết Bản Ghi', padding='10')
        detail_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        
        self.history_detail_text = tk.Text(detail_frame, height=10, width=80, font=('Consolas', 10), wrap=tk.WORD, bg='#1e1e1e', fg='#d4d4d4')
        self.history_detail_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        detail_scroll = ttk.Scrollbar(detail_frame, orient=tk.VERTICAL, command=self.history_detail_text.yview)
        detail_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.history_detail_text.config(yscrollcommand=detail_scroll.set)
        
        # Configure text tags for formatting
        self.history_detail_text.tag_config('header', font=('Consolas', 10, 'bold'), foreground='#4ec9b0')
        self.history_detail_text.tag_config('conclusion', font=('Consolas', 11, 'bold'), foreground='#f48771')
        self.history_detail_text.tag_config('value', font=('Consolas', 10), foreground='#d4d4d4')
        self.history_detail_text.tag_config('path_link', underline=True, foreground='#569cd6')
        
        # Bind click event for path copy
        self.history_detail_text.bind('<Button-1>', self.on_path_click)
        
        # Store current path for copy action
        self.current_file_path = None
        
        # Configure grid weights
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(1, weight=1)
        history_frame.rowconfigure(2, weight=1)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        detail_frame.columnconfigure(0, weight=1)
        detail_frame.rowconfigure(0, weight=1)
        
        # Load history on first display
        self.refresh_history()
    
    def refresh_history(self):
        """Refresh scan history from database"""
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Get history from database
        history = self.app.get_scan_history(limit=100)
        
        for record in history:
            scan_time = record.get('scan_timestamp', 'N/A')
            file_name = record.get('file_name', 'N/A')
            file_path = record.get('file_path', 'N/A')
            risk_level_en = record.get('risk_level', 'N/A')
            risk_level_vi = translate_risk_level(risk_level_en)
            risk_score_val = record.get('risk_score', 'N/A')
            # Format risk_score to int if it's a number
            if isinstance(risk_score_val, (int, float)) and risk_score_val != 'N/A':
                risk_score = int(risk_score_val)
            else:
                risk_score = risk_score_val
            
            self.history_tree.insert(
                '',
                'end',
                values=(scan_time, file_name, file_path, risk_level_vi, risk_score),
                tags=(risk_level_en,)
            )
        
        # Configure tags for colors
        self.history_tree.tag_configure('LOW', background='lightgreen')
        self.history_tree.tag_configure('MEDIUM', background='lightyellow')
        self.history_tree.tag_configure('HIGH', background='lightcoral')
        self.history_tree.tag_configure('CRITICAL', background='red', foreground='white')
    
    def on_history_select(self, event):
        """Handle history record selection"""
        selection = self.history_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.history_tree.item(item)['values']
        
        # Get full record from database based on values
        history = self.app.get_scan_history(limit=100)
        
        for record in history:
            if (record.get('scan_timestamp') == values[0] and 
                record.get('file_name') == values[1]):
                
                # Display details
                detail_text = self.history_detail_text
                detail_text.delete(1.0, tk.END)
                
                # Format output with tags
                detail_text.insert(tk.END, '==================================================\n', 'conclusion')
                detail_text.insert(tk.END, 'CHI TIẾT BẢN GHI QUÉT\n', 'header')
                detail_text.insert(tk.END, '==================================================\n\n', 'conclusion')
                
                detail_text.insert(tk.END, '📄 Tên tập tin: ', 'header')
                detail_text.insert(tk.END, f"{record.get('file_name')}\n", 'value')
                
                detail_text.insert(tk.END, '📁 Đường dẫn: ', 'header')
                path_text = record.get('file_path')
                detail_text.insert(tk.END, path_text, ('value', 'path_link'))
                detail_text.insert(tk.END, '\n', 'value')
                
                detail_text.insert(tk.END, '📊 Kích thước: ', 'header')
                detail_text.insert(tk.END, f"{record.get('file_size', 'N/A')} bytes\n", 'value')
                
                detail_text.insert(tk.END, '📝 Phần mở rộng: ', 'header')
                detail_text.insert(tk.END, f"{record.get('file_extension', 'N/A')}\n", 'value')
                
                detail_text.insert(tk.END, '🔐 Mã hash: ', 'header')
                detail_text.insert(tk.END, f"{record.get('file_hash', 'N/A')}\n", 'value')
                
                detail_text.insert(tk.END, '⚠️  Mức độ rủi ro: ', 'header')
                risk_level_vi = translate_risk_level(record.get('risk_level', 'N/A'))
                detail_text.insert(tk.END, f"{risk_level_vi}\n", 'value')
                
                detail_text.insert(tk.END, '📈 Điểm rủi ro: ', 'header')
                score_val = record.get('risk_score', 'N/A')
                score_display = int(score_val) if isinstance(score_val, (int, float)) else score_val
                detail_text.insert(tk.END, f"{score_display}/10\n", 'value')
                
                detail_text.insert(tk.END, '⏰ Thời gian quét: ', 'header')
                detail_text.insert(tk.END, f"{record.get('scan_timestamp', 'N/A')}\n", 'value')
                
                detail_text.insert(tk.END, '\n==================================================\n', 'conclusion')
                detail_text.insert(tk.END, '✅ KẾT LUẬN:', 'conclusion')
                detail_text.insert(tk.END, '\n====>✅ ', 'conclusion')
                
                # Add conclusion based on risk level
                risk_level = record.get('risk_level', 'N/A')
                if risk_level == 'LOW':
                    detail_text.insert(tk.END, 'TẬP TIN AN TOÀN - CÓ THỂ MỞ\n', 'value')
                elif risk_level == 'MEDIUM':
                    detail_text.insert(tk.END, 'TẬP TIN CÓ NGUY HIỂM - CẢNH BÁO!\n', 'conclusion')
                elif risk_level == 'HIGH':
                    detail_text.insert(tk.END, 'TẬP TIN NGUY HIỂM - KHÔNG MỞ!\n', 'conclusion')
                elif risk_level == 'CRITICAL':
                    detail_text.insert(tk.END, 'TẬP TIN LÀ MALWARE - NGAY LẬP TỨC XÓA!\n', 'conclusion')
                
                detail_text.insert(tk.END, '==================================================\n', 'conclusion')
                
                # Store path for click event
                self.current_file_path = record.get('file_path')
                break
    
    def on_path_click(self, event):
        """Handle click on path link to copy to clipboard"""
        # Get the position of the click
        widget = event.widget
        index = widget.index(f'@{event.x},{event.y}')
        
        # Check if clicked text has path_link tag
        if 'path_link' in widget.tag_names(index):
            # Copy path to clipboard
            if self.current_file_path:
                self.root.clipboard_clear()
                self.root.clipboard_append(self.current_file_path)
                self.root.update()  # Keep clipboard after window is gone
                messagebox.showinfo('Thành công', f'Đã copy đường dẫn:\n{self.current_file_path}')
    
    def delete_history_record(self):
        """Delete selected history record"""
        selection = self.history_tree.selection()
        if not selection:
            messagebox.showwarning('Cảnh báo', 'Vui lòng chọn một bản ghi để xóa')
            return
        
        if messagebox.askyesno('Xác nhận', 'Bạn có chắc muốn xóa bản ghi này?'):
            # For now, just refresh. Full delete would require ID management
            messagebox.showinfo('Thông tin', 'Tính năng xóa sẽ được triển khai sau')
    
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
            # Refresh history after scan
            self.refresh_history()
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
        output.append(f'Điểm rủi ro: {int(risk_info.get("total_score", 0))}/10')
        output.append(f'Mức độ rủi ro: {risk_info.get("level")}')
        
        output.append('')
        output.append('KẾT QUẢ PHÂN TÍCH')
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
        output.append('KHUYẾN NGHỊ')
        output.append('-'*70)
        output.append(report.get('recommendation', 'Không có'))
        
        output.append('')
        output.append('HÀNH ĐỘNG ĐƯỢ KHUYẾN NGHỊ')
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
