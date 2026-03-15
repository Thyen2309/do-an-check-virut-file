"""
Magic Number (File Signature) Database
Define file signatures to detect file types
"""

# Mapping: magic_bytes -> (file_type, expected_extensions)
MAGIC_NUMBERS = {
    # Executables & Archives
    b'\x4d\x5a': ('PE Executable', ('exe', 'dll', 'com', 'scr', 'sys')),
    b'\x50\x4b\x03\x04': ('ZIP Archive', ('zip', 'docx', 'xlsx', 'pptx', 'jar', 'apk')),
    b'\x1f\x8b': ('GZIP', ('gz', 'gzip')),
    b'\x42\x4d': ('Bitmap Image', ('bmp',)),
    b'\xff\xd8\xff': ('JPEG Image', ('jpg', 'jpeg')),
    b'\x89PNG\r\n\x1a\n': ('PNG Image', ('png',)),
    b'%PDF': ('PDF Document', ('pdf',)),
    b'\x7fELF': ('ELF Binary', ('elf', 'so')),
    b'\xca\xfe\xba\xbe': ('Java Class', ('class',)),
    b'BZh': ('BZIP2', ('bz2',)),
    b'\xfd7zXZ\x00': ('7-Zip', ('7z',)),
    b'Rar!': ('RAR Archive', ('rar',)),
    
    # Documents
    b'\xd0\xcf\x11\xe0': ('OLE Document', ('doc', 'xls', 'ppt', 'msg')),
    b'PK\x03\x04': ('Office Open XML', ('docx', 'xlsx', 'pptx')),
    
    # Media
    b'\xff\xfb': ('MP3 Audio', ('mp3',)),
    b'ID3': ('MP3 Audio', ('mp3',)),
    b'\x00\x00\x00\x18ftypmp42': ('MPEG4 Video', ('mp4',)),
    b'ftyp': ('MPEG4 Video', ('mp4', 'mov')),
    b'\x52\x49\x46\x46': ('WAV Audio', ('wav',)),
    
    # Others
    b'<?xml': ('XML Document', ('xml',)),
    b'{': ('JSON Document', ('json',)),
    b'#!/': ('Shell Script', ('sh', 'bash')),
}


def detect_file_type(file_bytes: bytes) -> tuple:
    """
    Phát hiện loại file từ magic number
    
    Args:
        file_bytes: First N bytes của file
        
    Returns:
        (file_type, expected_extensions) hoặc (None, None)
    """
    for magic_sig, (file_type, extensions) in MAGIC_NUMBERS.items():
        if file_bytes.startswith(magic_sig):
            return file_type, extensions
    
    return None, None


def get_dangerous_signatures() -> list:
    """
    Lấy danh sách file signature nguy hiểm
    
    Returns:
        List of dangerous file types
    """
    dangerous = [
        'PE Executable',  # .exe, .dll
        'ELF Binary',      # Linux executables
        'Java Class',      # .class files
    ]
    return dangerous
