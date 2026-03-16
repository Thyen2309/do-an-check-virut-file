"""Application constants"""

APP_NAME = 'File Security Checker'
APP_VERSION = '1.0.0'

# File size constants (in bytes)
KB = 1024
MB = KB * 1024
GB = MB * 1024

# Risk levels
RISK_LEVEL_LOW = 'LOW'
RISK_LEVEL_MEDIUM = 'MEDIUM'
RISK_LEVEL_HIGH = 'HIGH'
RISK_LEVEL_CRITICAL = 'CRITICAL'

# File analysis defaults
DEFAULT_CHUNK_SIZE = 4096
DEFAULT_MAX_FILE_SIZE = 500 * MB

# Supported hash algorithms
HASH_ALGORITHMS = ['sha256', 'sha1', 'md5']
DEFAULT_HASH_ALGO = 'sha256'

# Dangerous extensions
DANGEROUS_EXTENSIONS = {
    'exe', 'dll', 'com', 'scr', 'vbs', 'js', 'jse',
    'bat', 'cmd', 'ps1', 'psc1', 'msh', 'msh1', 'msh2', 'mshxml',
    'msh1xml', 'msh2xml', 'sh', 'app', 'msi', 'psz', 'mst', 'ocx',
    'cpl', 'hta', 'sct', 'scr', 'pif', 'jar', 'apk'
}

# Safe extensions
SAFE_EXTENSIONS = {
    'txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
    'jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'tiff', 'webp',
    'mp3', 'mp4', 'mov', 'avi', 'mkv', 'flv', 'wav', 'flac',
    'csv', 'json', 'xml', 'html', 'htm', 'css', 'log', 'md'
}
