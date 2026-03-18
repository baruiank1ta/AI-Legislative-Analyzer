import os
import streamlit as st

# ============================================
# OPENROUTER API CONFIGURATION
# ============================================

def get_api_key():
    """Get API key from Streamlit secrets (Cloud) or environment (Local)"""
    # Try Streamlit Cloud first
    try:
        api_key = st.secrets.get("OPENROUTER_API_KEY")
        if api_key:
            return api_key
    except:
        pass
    
    # Try environment variable (local development)
    api_key = os.getenv("OPENROUTER_API_KEY")
    if api_key:
        return api_key
    
    # Not found
    return None

OPENROUTER_API_KEY = get_api_key()
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
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
# FILE SETTINGS
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
# VALIDATION - Show error only when needed
# ============================================
# Don't raise error here - handle in main.py instead
if not OPENROUTER_API_KEY:
    pass  # Will be handled in main.py
