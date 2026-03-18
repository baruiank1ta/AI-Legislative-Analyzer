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
# TOKEN COMPRESSOR
# ===============================
class TokenCompressor:
    def __init__(self):
        self.stopwords = set()

    def compress_text(self, text: str) -> Dict:
        """Compress text by keeping key sentences"""
        try:
            original_tokens = len(text.split())
            
            # Better compression: extract key sentences
            sentences = text.split('.')
            important_sentences = []
            
            keywords = ['shall', 'must', 'require', 'prohibit', 'amend', 'penalty', 'fine', 'section']
            
            for sent in sentences:
                if any(kw in sent.lower() for kw in keywords):
                    important_sentences.append(sent.strip())
            
            # If we found important sentences, use them; otherwise use first 30%
            if important_sentences:
                compressed = '. '.join(important_sentences[:50])  # Keep top 50 important sentences
            else:
                compressed = text[:int(len(text) * COMPRESSION_RATIO)]
            
            # Ensure we have some text
            if not compressed or len(compressed.split()) < 10:
                compressed = text[:int(len(text) * 0.5)]
            
            compressed_tokens = len(compressed.split())

            return {
                'original_tokens': original_tokens,
                'compressed_tokens': compressed_tokens,
                'compression_ratio': round(
                    (1 - compressed_tokens/original_tokens) * 100, 2
                ) if original_tokens > 0 else 0,
                'compressed_text': compressed
            }
        except Exception as e:
            # Fallback: just use original text
            tokens = len(text.split())
            return {
                'original_tokens': tokens,
                'compressed_tokens': tokens,
                'compression_ratio': 0,
                'compressed_text': text[:int(len(text) * 0.3)]
            }

# ===============================
# DOCUMENT PROCESSOR
# ===============================
class DocumentProcessor:

    @staticmethod
    def extract_text(file_path: str, file_type: str) -> str:
        """Extract text from various file types"""
        try:
            if file_type == "pdf":
                with open(file_path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    text = ""
                    for page in reader.pages:
                        extracted = page.extract_text()
                        if extracted:
                            text += extracted + "\n"
                    return text if text else "Could not extract text from PDF"

            elif file_type == "docx":
                doc = docx.Document(file_path)
                text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
                return text if text else "Could not extract text from DOCX"

            elif file_type == "txt":
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
                    return text if text else "Text file is empty"

            else:
                raise ValueError(f"Unsupported file type: {file_type}")
                
        except Exception as e:
            raise Exception(f"Error extracting text: {str(e)}")

# ===============================
# LEGISLATIVE ANALYZER (FIXED FOR CLOUD)
# ===============================
class LegislativeAnalyzer:

    def __init__(self):
        if not OPENROUTER_API_KEY:
            raise ValueError(
                "❌ API Key not configured!\n"
                "For Streamlit Cloud: Add to Secrets panel\n"
                "For Local: Add to .env file"
            )

        self.conversation_history = []
        self.current_document = None
        self.compressor = TokenCompressor()
        self.api_key = OPENROUTER_API_KEY
        self.base_url = OPENROUTER_BASE_URL
        self.model = MODEL
        self.max_tokens = MAX_TOKENS

    def analyze_document(self, document_text: str, analysis_type: str) -> Dict:
        """Analyze a legal document"""
        try:
            if not document_text or len(document_text.strip()) < 10:
                raise ValueError("Document text is too short")
            
            self.current_document = document_text

            # Compress the document
            compression = self.compressor.compress_text(document_text)
            
            if not compression['compressed_text']:
                raise ValueError("Could not compress document")

            # Create analysis prompt
            analysis_prompts = {
                'Summary': f"Provide a clear citizen-friendly summary of this document:\n\n{compression['compressed_text']}",
                'Key Changes': f"List the key changes in this document:\n\n{compression['compressed_text']}",
                'Impact Assessment': f"Assess the impact of this document on citizens:\n\n{compression['compressed_text']}",
                'Comparison': f"Compare this with existing related documents:\n\n{compression['compressed_text']}",
                'Implementation': f"Explain how this will be implemented:\n\n{compression['compressed_text']}"
            }

            prompt = analysis_prompts.get(analysis_type, analysis_prompts['Summary'])

            # Call OpenRouter API
            result = self._call_openrouter(prompt)

            return {
                "analysis": result,
                "original_tokens": compression["original_tokens"],
                "compressed_tokens": compression["compressed_tokens"],
                "compression_ratio": compression["compression_ratio"],
                "analysis_type": analysis_type
            }
            
        except Exception as e:
            raise Exception(f"Document analysis failed: {str(e)}")

    def _call_openrouter(self, prompt: str) -> str:
        """Call OpenRouter API with proper error handling"""
        try:
            # Add message to history
            self.conversation_history.append({
                "role": "user",
                "content": prompt
            })

            # Prepare API call
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/baruiankita/AI-Legislative-Analyzer",
                "X-Title": "AI Legislative Analyzer"
            }

            payload = {
                "model": self.model,
                "messages": self.conversation_history,
                "max_tokens": min(self.max_tokens, 1500),
                "temperature": 0.7
            }

            # Make API request with timeout
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=120  # 2 minute timeout for Streamlit Cloud
            )

            # Check response status
            if response.status_code != 200:
                error_msg = f"API Error {response.status_code}"
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_msg = error_data["error"].get("message", error_msg)
                except:
                    pass
                raise Exception(error_msg)

            # Parse response
            data = response.json()

            # Check for API errors
            if "error" in data:
                error_msg = data.get("error", {})
                if isinstance(error_msg, dict):
                    raise Exception(error_msg.get("message", "Unknown API error"))
                else:
                    raise Exception(str(error_msg))

            # Extract answer
            if "choices" not in data or len(data["choices"]) == 0:
                raise Exception("No response from API")

            answer = data["choices"][0].get("message", {}).get("content")
            
            if not answer:
                raise Exception("Empty response from API")

            # Add to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": answer
            })

            return answer

        except requests.exceptions.Timeout:
            raise Exception(
                "❌ API Request Timeout\n"
                "The request took too long. Try with a smaller document."
            )
        except requests.exceptions.ConnectionError:
            raise Exception(
                "❌ Connection Error\n"
                "Cannot reach OpenRouter. Check your internet connection."
            )
        except requests.exceptions.RequestException as e:
            raise Exception(f"❌ Network Error: {str(e)}")
        except Exception as e:
            raise Exception(f"❌ API Call Failed: {str(e)}")

    def follow_up_question(self, question: str) -> str:
        """Ask a follow-up question about the document"""
        try:
            if not self.current_document:
                raise ValueError("No document loaded for follow-up questions")
            
            if not question or len(question.strip()) < 3:
                raise ValueError("Question is too short")
            
            return self._call_openrouter(question)
        except Exception as e:
            raise Exception(f"Follow-up question failed: {str(e)}")

    def reset_conversation(self):
        """Reset the conversation and document"""
        self.conversation_history = []
        self.current_document = None


# ===============================
# HELPER FUNCTIONS
# ===============================
def estimate_tokens(text: str) -> int:
    """Estimate token count (roughly 1 token per 4 characters)"""
    return max(len(text) // 4, 1)

def format_text_output(text: str) -> str:
    """Format text for better readability"""
    return text
