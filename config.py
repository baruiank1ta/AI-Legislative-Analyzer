import os
import streamlit as st

# ============================================
# OPENROUTER API CONFIGURATION (WORKS EVERYWHERE)
# ============================================

def get_api_key():
    """
    Get API key from Streamlit secrets (for deployment)
    OR fallback to .env (for local)
    """
    try:
        # Streamlit Cloud
        return st.secrets["OPENROUTER_API_KEY"]
    except:
        # Local development
        return os.getenv("OPENROUTER_API_KEY")

OPENROUTER_API_KEY = get_api_key()

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Best FREE model
MODEL = "openrouter/free"

MAX_TOKENS = 1500

# ============================================
# TOKEN COMPRESSION SETTINGS
# ============================================
COMPRESSION_RATIO = 0.3
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
    raise ValueError(
        "❌ OPENROUTER_API_KEY not found!\n"
        "👉 For Streamlit Cloud: Add it in Secrets\n"
        "👉 For Local: Add it in .env file\n"
        "Get your free key from: https://openrouter.ai"
    )
