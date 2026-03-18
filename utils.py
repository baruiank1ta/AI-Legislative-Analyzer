import os
import re
from typing import List, Dict, Tuple
from openai import OpenAI
import PyPDF2
import docx
from config import (
    OPENROUTER_API_KEY, OPENROUTER_BASE_URL, MODEL, MAX_TOKENS,
    COMPRESSION_RATIO, MIN_CHUNK_SIZE, MAX_CHUNK_SIZE
)

class TokenCompressor:
    """Compress legal documents while maintaining essential information"""
    
    def __init__(self):
        self.stopwords = self._load_stopwords()
    
    def _load_stopwords(self) -> set:
        """Load common legal stopwords to remove"""
        return {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'are', 'was', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'can', 'shall'
        }
    
    def compress_text(self, text: str) -> Dict:
        """
        Compress document text using multiple strategies
        
        Returns:
            Dict with original_tokens, compressed_tokens, and compressed_text
        """
        # Step 1: Clean and normalize
        cleaned = self._clean_text(text)
        
        # Step 2: Extract key sentences
        key_sentences = self._extract_key_sentences(cleaned)
        
        # Step 3: Remove redundancy
        compressed = self._remove_redundancy(key_sentences)
        
        # Step 4: Token count estimation
        original_tokens = len(text.split())
        compressed_tokens = len(compressed.split())
        
        return {
            'original_tokens': original_tokens,
            'compressed_tokens': compressed_tokens,
            'compression_ratio': round(
                (1 - compressed_tokens/original_tokens) * 100, 2
            ),
            'compressed_text': compressed
        }
    
    def _clean_text(self, text: str) -> str:
        """Remove formatting, extra spaces, and boilerplate"""
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers and headers/footers
        text = re.sub(r'Page \d+|^\s*\d+\s*$', '', text, flags=re.MULTILINE)
        
        # Remove common legal boilerplate
        boilerplate = [
            r'The Government of India.*?hereby declares',
            r'In exercise of the powers conferred.*?Constitution',
            r'No part of this.*?permission',
            r'whereas',
            r'preamble',
        ]
        for pattern in boilerplate:
            text = re.sub(pattern, '[BOILERPLATE]', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def _extract_key_sentences(self, text: str) -> str:
        """Extract sentences with keywords related to laws"""
        keywords = [
            'shall', 'must', 'require', 'prohibit', 'amend', 'repeal',
            'provide', 'establish', 'create', 'define', 'penalty', 'fine',
            'punishment', 'offense', 'crime', 'entitle', 'exempt', 'section',
            'rule', 'regulation', 'clause', 'article', 'schedule'
        ]
        
        sentences = re.split(r'[.!?]+', text)
        key_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and any(kw in sentence.lower() for kw in keywords):
                key_sentences.append(sentence)
        
        return '. '.join(key_sentences) + '.'
    
    def _remove_redundancy(self, text: str) -> str:
        """Remove repeated phrases and redundant information"""
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        
        # Remove near-duplicates
        unique_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and not self._is_duplicate(sentence, unique_sentences):
                unique_sentences.append(sentence)
        
        return '. '.join(unique_sentences[:150])  # Keep top 150 sentences
    
    def _is_duplicate(self, sentence: str, existing: List[str]) -> bool:
        """Check if sentence is duplicate of existing ones"""
        sentence_words = set(sentence.lower().split())
        
        for existing_sent in existing:
            existing_words = set(existing_sent.lower().split())
            
            # Calculate similarity
            if len(sentence_words) > 0:
                overlap = len(sentence_words & existing_words)
                similarity = overlap / len(sentence_words)
                
                if similarity > 0.7:  # More than 70% similar
                    return True
        
        return False


class DocumentProcessor:
    """Extract text from various document formats"""
    
    @staticmethod
    def extract_from_pdf(file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text()
            return text
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
    
    @staticmethod
    def extract_from_docx(file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text
        except Exception as e:
            raise Exception(f"Error reading DOCX: {str(e)}")
    
    @staticmethod
    def extract_from_txt(file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            raise Exception(f"Error reading TXT: {str(e)}")
    
    @staticmethod
    def extract_text(file_path: str, file_type: str) -> str:
        """Main method to extract text based on file type"""
        if file_type.lower() == 'pdf':
            return DocumentProcessor.extract_from_pdf(file_path)
        elif file_type.lower() == 'docx':
            return DocumentProcessor.extract_from_docx(file_path)
        elif file_type.lower() == 'txt':
            return DocumentProcessor.extract_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")


class LegislativeAnalyzer:
    """Main class for legislative analysis using OpenRouter API (100% FREE!)"""
    
    def __init__(self):
        if not OPENROUTER_API_KEY:
            raise ValueError(
                "OPENROUTER_API_KEY not found in environment variables.\n"
                "Get your FREE key from: https://openrouter.ai\n"
                "Then add it to your .env file: OPENROUTER_API_KEY=your_key"
            )
        
        # Initialize OpenAI client with OpenRouter settings
        self.client = OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL
        )
        self.compressor = TokenCompressor()
        self.conversation_history = []
        self.current_document = None
    
    def analyze_document(self, document_text: str, analysis_type: str) -> Dict:
        """
        Analyze a legal document
        
        Args:
            document_text: The document content
            analysis_type: Type of analysis to perform
        
        Returns:
            Dict with analysis results and token metrics
        """
        self.current_document = document_text
        
        # Step 1: Compress the document
        compression_result = self.compressor.compress_text(document_text)
        compressed_text = compression_result['compressed_text']
        
        # Step 2: Prepare the prompt
        prompt = self._prepare_prompt(compressed_text, analysis_type)
        
        # Step 3: Call OpenRouter API
        response = self._call_openrouter(prompt)
        
        return {
            'analysis': response,
            'original_tokens': compression_result['original_tokens'],
            'compressed_tokens': compression_result['compressed_tokens'],
            'compression_ratio': compression_result['compression_ratio'],
            'analysis_type': analysis_type
        }
    
    def _prepare_prompt(self, compressed_text: str, analysis_type: str) -> str:
        """Prepare prompt for OpenRouter"""
        analysis_prompts = {
            'Summary': f"""Analyze this Indian law/bill and provide a clear summary 
that a common citizen can understand. Use simple language, avoid legal jargon.

Document Content:
{compressed_text}

Please provide:
1. What is this law about? (1-2 sentences)
2. Who does it affect?
3. What are the main rules or requirements?
4. When does it come into effect?

Answer in simple, easy-to-understand language.""",
            
            'Key Changes': f"""Identify the key changes this bill proposes.

Document Content:
{compressed_text}

List the main changes with brief explanations. Format as a numbered list.""",
            
            'Impact Assessment': f"""Assess the potential impact of this legislation on citizens.

Document Content:
{compressed_text}

Analyze and provide:
1. Positive impacts - Who benefits
2. Potential challenges - What difficulties might arise
3. Who benefits most
4. Who might be negatively affected

Use simple language.""",
            
            'Comparison': f"""Compare this legislation with existing related laws.

Document Content:
{compressed_text}

Explain:
1. How this compares to existing legislation
2. What is new or different
3. Any overlaps with existing laws""",
            
            'Implementation': f"""Explain how this law will be implemented in practical terms.

Document Content:
{compressed_text}

Describe:
1. Which government bodies are responsible
2. Timeline for implementation
3. What actions citizens/organizations need to take
4. What are the penalties for non-compliance

Use simple language that citizens can understand."""
        }
        
        return analysis_prompts.get(analysis_type, analysis_prompts['Summary'])
    
    def _call_openrouter(self, prompt: str) -> str:
        """Call OpenRouter API with conversation history (100% FREE!)"""
        self.conversation_history.append({
            'role': 'user',
            'content': prompt
        })
        
        try:
            response = self.client.chat.completions.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                messages=self.conversation_history,
                temperature=0.7
            )
            
            assistant_message = response.choices[0].message.content
            self.conversation_history.append({
                'role': 'assistant',
                'content': assistant_message
            })
            
            return assistant_message
        except Exception as e:
            raise Exception(f"OpenRouter API Error: {str(e)}")
    
    def follow_up_question(self, question: str) -> str:
        """Ask a follow-up question about previous analysis"""
        if not self.current_document:
            raise ValueError("No document loaded. Please analyze a document first.")
        
        # Add context about the current document
        contextual_question = f"""Based on the previously analyzed legal document, 
please answer this question:

{question}

Provide a clear, concise answer using simple language."""
        
        return self._call_openrouter(contextual_question)
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []
        self.current_document = None


def estimate_tokens(text: str) -> int:
    """
    Rough estimation of tokens (1 token ≈ 4 characters)
    This is a simplified estimate.
    """
    return max(len(text) // 4, 1)


def format_text_output(text: str) -> str:
    """Format text for better readability in Streamlit"""
    return text.replace('\n\n', '\n\n> ').replace('\n', '  \n')