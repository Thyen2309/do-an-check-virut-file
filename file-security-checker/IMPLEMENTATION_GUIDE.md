# File Security Checker - Implementation Guide

## 📋 Hướng Dẫn Chi Tiết Triển Khai

### Phase 1: Cơ Bản (MVP - 2 tuần)

#### Tuần 1: Setup & Core Logic
- [x] Tạo project structure
- [x] Implement FileAnalyzer:
  - [x] Extension checking
  - [x] Magic number detection
  - [x] Size analysis
  - [x] Double extension detection
- [x] Implement HashManager:
  - [x] SHA256 calculation
  - [x] Hash comparison
  - [x] Database integration
- [x] Implement RiskScorer:
  - [x] Weighted scoring algorithm
  - [x] Risk level classification
  - [x] Recommendation generation

#### Tuần 2: GUI & Database
- [x] Implement DatabaseManager:
  - [x] SQLite schema
  - [x] Scan history storage
  - [x] Dangerous hash database
  - [x] Whitelist management
- [x] Implement GUI (Tkinter):
  - [x] File selection
  - [x] Scan display
  - [x] Result formatting
- [x] Testing & Debugging

### Phase 2: Enhancement (Optional - 1 tuần)

#### Advanced Features:
1. **Behavioral Analysis (Heuristics)**
   - PE file analysis
   - Packing detection
   - Suspicious API detection
   - Code injection indicators

2. **File Quarantine**
   - Auto-isolation of dangerous files
   - Encryption (optional)
   - Restore functionality
   - Audit logging

3. **Cloud Integration** (Optional)
   - VirusTotal API integration
   - Hybrid Analysis
   - Auto-updates

### Phase 3: Polish (Optional - 1 tuần)

- [ ] Improve GUI UX
- [ ] Add dark theme
- [ ] Multi-language support
- [ ] Performance optimization
- [ ] Comprehensive documentation

---

## 🔧 Công Cụ & Công Nghệ

### Python Packages

**Core:**
- `hashlib` (built-in) - File hashing
- `sqlite3` (built-in) - Database
- `os, pathlib` (built-in) - File operations
- `json` (built-in) - Configuration
- `logging` (built-in) - Logging

**GUI:**
- `tkinter` (built-in) - GUI framework

**Optional Enhancements:**
- `python-magic` - Advanced file type detection
- `pycryptodome` - Encryption for quarantine
- `requests` - Cloud API integration

### Development Tools
- `pytest` - Unit testing
- `pylint` - Code quality
- `black` - Code formatting
- `sqlite3` - Database management

---

## 📊 Database Schema Details

### scan_history
```sql
CREATE TABLE scan_history (
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
    details TEXT  -- Full JSON analysis
);
```

### dangerous_hashes
```sql
CREATE TABLE dangerous_hashes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_hash VARCHAR(64) UNIQUE NOT NULL,
    threat_name TEXT,
    threat_category TEXT,
    severity INTEGER,
    added_date DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### whitelist
```sql
CREATE TABLE whitelist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_hash VARCHAR(64) UNIQUE NOT NULL,
    file_name TEXT,
    file_path TEXT,
    added_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    reason TEXT
);
```

---

## 🚀 Chạy Ứng Dụng

### 1. Setup Environment
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### 2. Run CLI Version
```bash
python src/main.py "C:\Downloads\file.exe"
```

### 3. Run GUI Version
```bash
python src/gui.py
```

### 4. Run Tests
```bash
pytest tests/
pytest --cov=src tests/
```

---

## 📈 Performance Benchmarks

| Operation | Time | Memory |
|-----------|------|--------|
| Small file scan (1MB) | ~50ms | ~5MB |
| Medium file scan (10MB) | ~150ms | ~10MB |
| Large file scan (100MB) | ~800ms | ~15MB |
| Hash calculation | Included above | 1MB |
| Database query | ~5ms | Minimal |

### Optimization Tips
1. **Chunk-based file reading** - Không load toàn bộ file vào memory
2. **Index database queries** - Tối ưu hóa search
3. **Lazy loading** - Load malware DB on demand
4. **Caching** - Cache frequently checked hashes

---

## 🧪 Testing Strategy

### Unit Tests
```python
# Test file analyzer
test_check_dangerous_extension()
test_check_safe_extension()
test_magic_number_detection()
test_double_extension_detection()

# Test hash manager
test_calculate_hash()
test_add_dangerous_hash()
test_whitelist_functionality()

# Test risk scorer
test_risk_level_classification()
test_score_calculation()
test_reason_generation()
```

### Integration Tests
```python
# Full scan workflow
test_complete_scan_workflow()
test_database_storage()
test_history_retrieval()
```

---

## 🛠️ Troubleshooting

### Common Issues

1. **tkinter not found** (on Linux)
   ```bash
   sudo apt-get install python3-tk
   ```

2. **sqlite3 errors**
   - Verify database path exists
   - Check file permissions
   - Ensure schema is initialized

3. **Performance issues**
   - Don't scan network drives
   - Check disk speed
   - Close other applications

---

## 📚 Thêm Resources

- [Python Security Best Practices](https://owasp.org/)
- [YARA Rules for Malware Detection](https://virustotal.github.io/yara/)
- [Magic Numbers Database](http://www.garykessler.net/library/file_sigs.html)
- [VirusTotal API](https://developers.virustotal.com/reference/)

---

**Last Updated:** 2024-03-16  
**Version:** 1.0.0
