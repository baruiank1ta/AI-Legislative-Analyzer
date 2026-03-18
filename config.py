import os
from dotenv import load_dotenv

load_dotenv()

# ============================================
# OPENROUTER API CONFIGURATION (100% FREE!)
# ============================================
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Best model for legal documents - COMPLETELY FREE!
MODEL = "openrouter/free"

# Alternative free models you can use:
# - "meta-llama/llama-2-7b-chat:free" - Good alternative
# - "gryphe/mythomist-7b:free" - Another option
# All are completely FREE with no rate limits!

MAX_TOKENS = 1500

# ============================================
# TOKEN COMPRESSION SETTINGS
# ============================================
COMPRESSION_RATIO = 0.3  # Keep 30% of tokens
MIN_CHUNK_SIZE = 500
MAX_CHUNK_SIZE = 2000

# ============================================
# APP CONFIGURATION
# ============================================
APP_TITLE = "🏛️ AI Legislative Analyzer"
APP_SUBTITLE = "Simplifying Indian Laws & Parliamentary Bills"

# ============================================
# FILE UPLOAD SETTINGS
# ============================================
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx'}
MAX_FILE_SIZE = 50 * 1024 * 1024

# ============================================
# ANALYSIS TYPES
# ============================================
ANALYSIS_TYPES = {
    'Summary': 'Provide a clear, citizen-friendly summary',
    'Key Changes': 'Identify the main changes this bill proposes',
    'Impact Assessment': 'Analyze potential impact on citizens',
    'Comparison': 'Compare with existing related laws',
    'Implementation': 'Explain how this will be implemented'
}

# ============================================
# COMPRESSION ENGINE SETTINGS
# ============================================
ENABLE_COMPRESSION = True
COMPRESSION_MIN_TOKENS = 5000

# ============================================
# VALIDATION
# ============================================
if not OPENROUTER_API_KEY:
    print("⚠️ WARNING: OPENROUTER_API_KEY not found in .env file!")
    print("Get your free API key from: https://openrouter.ai")