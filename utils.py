import os
import re
import requests
from typing import List, Dict
import PyPDF2
import docx
from config import (
    OPENROUTER_API_KEY, OPENROUTER_BASE_URL, MODEL, MAX_TOKENS,
    COMPRESSION_RATIO, MIN_CHUNK_SIZE, MAX_CHUNK_SIZE
)

# ===============================
# TOKEN COMPRESSOR (same)
# ===============================
class TokenCompressor:
    def __init__(self):
        self.stopwords = set()

    def compress_text(self, text: str) -> Dict:
        original_tokens = len(text.split())
        compressed = text[:int(len(text) * COMPRESSION_RATIO)]
        compressed_tokens = len(compressed.split())

        return {
            'original_tokens': original_tokens,
            'compressed_tokens': compressed_tokens,
            'compression_ratio': round(
                (1 - compressed_tokens/original_tokens) * 100, 2
            ),
            'compressed_text': compressed
        }

# ===============================
# DOCUMENT PROCESSOR (same)
# ===============================
class DocumentProcessor:

    @staticmethod
    def extract_text(file_path: str, file_type: str) -> str:
        if file_type == "pdf":
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                return " ".join([p.extract_text() for p in reader.pages])

        elif file_type == "docx":
            doc = docx.Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs])

        elif file_type == "txt":
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()

        else:
            raise ValueError("Unsupported file type")

# ===============================
# LEGISLATIVE ANALYZER (FIXED)
# ===============================
class LegislativeAnalyzer:

    def __init__(self):
        if not OPENROUTER_API_KEY:
            raise ValueError("API Key missing")

        self.conversation_history = []
        self.current_document = None
        self.compressor = TokenCompressor()

    def analyze_document(self, document_text: str, analysis_type: str) -> Dict:
        self.current_document = document_text

        compression = self.compressor.compress_text(document_text)

        prompt = f"""
Analyze this legal document and provide a {analysis_type}:

{compression['compressed_text']}
"""

        result = self._call_openrouter(prompt)

        return {
            "analysis": result,
            "original_tokens": compression["original_tokens"],
            "compressed_tokens": compression["compressed_tokens"],
            "compression_ratio": compression["compression_ratio"],
            "analysis_type": analysis_type
        }

    def _call_openrouter(self, prompt: str) -> str:
        self.conversation_history.append({
            "role": "user",
            "content": prompt
        })

        response = requests.post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL,
                "messages": self.conversation_history,
                "max_tokens": MAX_TOKENS
            }
        )

        data = response.json()

        if "error" in data:
            raise Exception(data["error"]["message"])

        answer = data["choices"][0]["message"]["content"]

        self.conversation_history.append({
            "role": "assistant",
            "content": answer
        })

        return answer

    def follow_up_question(self, question: str) -> str:
        return self._call_openrouter(question)

    def reset_conversation(self):
        self.conversation_history = []
        self.current_document = None


# ===============================
# HELPERS
# ===============================
def estimate_tokens(text: str) -> int:
    return max(len(text) // 4, 1)

def format_text_output(text: str) -> str:
    return text
