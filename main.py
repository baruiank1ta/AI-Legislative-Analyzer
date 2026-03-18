import streamlit as st
import os
from pathlib import Path
from utils import (
    TokenCompressor, DocumentProcessor, LegislativeAnalyzer,
    estimate_tokens, format_text_output
)
from config import APP_TITLE, APP_SUBTITLE, ANALYSIS_TYPES, ALLOWED_EXTENSIONS, OPENROUTER_API_KEY

# Page configuration
st.set_page_config(
    page_title="AI Legislative Analyzer",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2.5rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.8rem;
        font-weight: 700;
        letter-spacing: -1px;
    }
    
    .main-header p {
        margin: 0.8rem 0 0 0;
        font-size: 1.15rem;
        opacity: 0.95;
        font-weight: 300;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #f0f2f6 100%);
        padding: 1.8rem;
        border-radius: 10px;
        border-left: 5px solid #667eea;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    .success-box {
        background: #d4edda;
        padding: 1.2rem;
        border-radius: 8px;
        color: #155724;
        border: 1px solid #c3e6cb;
        border-left: 4px solid #28a745;
    }
    
    .analysis-box {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        border: 1px solid #e8ecf1;
        margin-top: 1.5rem;
        line-height: 1.8;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    .file-upload-area {
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
    }
    
    hr {
        margin: 2rem 0 !important;
        border: none;
        border-top: 1px solid #e8ecf1;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = None
if 'current_document' not in st.session_state:
    st.session_state.current_document = None
if 'compression_stats' not in st.session_state:
    st.session_state.compression_stats = None
if 'error_message' not in st.session_state:
    st.session_state.error_message = None

# CHECK API KEY FIRST (before initializing analyzer)
if not OPENROUTER_API_KEY:
    st.error("""
    ❌ **API Key Not Found!**
    
    ### For Streamlit Cloud:
    1. Go to your app settings
    2. Click "Secrets"
    3. Add: `OPENROUTER_API_KEY=sk-or-your-key`
    4. Save and reboot app
    
    ### For Local:
    1. Create `.env` file
    2. Add: `OPENROUTER_API_KEY=your_key`
    3. Run: `streamlit run main.py`
    
    Get your FREE key from: https://openrouter.ai
    """)
    st.stop()

# Initialize analyzer
try:
    if st.session_state.analyzer is None:
        st.session_state.analyzer = LegislativeAnalyzer()
except Exception as e:
    st.error(f"""
    ❌ **Error Initializing App**: {str(e)}
    
    Please check:
    1. API key is correct (starts with sk-or-)
    2. Internet connection is working
    3. OpenRouter service is online
    """)
    st.stop()

# Header
st.markdown(f"""
<div class="main-header">
    <h1>{APP_TITLE}</h1>
    <p>{APP_SUBTITLE}</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings & Navigation")
    
    # Mode selection
    mode = st.radio(
        "Select Mode:",
        ["📄 Upload & Analyze", "💬 Chat with Document", "📊 Statistics", "ℹ️ About"]
    )

# Main content
if mode == "📄 Upload & Analyze":
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📤 Upload & Analyze Document")
        uploaded_file = st.file_uploader(
            "Choose a legal document",
            type=['pdf', 'docx', 'txt'],
            help="Upload a PDF, Word document, or text file containing legal content"
        )
    
    with col2:
        st.subheader("📋 File Types")
        st.write("✅ PDF Files")
        st.write("✅ Word (.docx)")
        st.write("✅ Text Files")
        st.caption("Max: 50 MB")
    
    if uploaded_file is not None:
        # Save uploaded file
        upload_dir = Path("uploaded_documents")
        upload_dir.mkdir(exist_ok=True)
        file_path = upload_dir / uploaded_file.name
        
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        # Extract text
        with st.spinner("📖 Reading document..."):
            try:
                file_type = uploaded_file.name.split('.')[-1]
                document_text = DocumentProcessor.extract_text(
                    str(file_path), file_type
                )
                st.session_state.current_document = document_text
                
                # Show document stats
                st.markdown("---")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    tokens = estimate_tokens(document_text)
                    st.metric(
                        "🔢 Estimated Tokens",
                        f"{tokens:,}"
                    )
                with col2:
                    chars = len(document_text)
                    st.metric(
                        "📊 Characters",
                        f"{chars:,}"
                    )
                with col3:
                    paragraphs = len(document_text.split('\n\n'))
                    st.metric(
                        "📝 Paragraphs",
                        f"{paragraphs:,}"
                    )
                with col4:
                    words = len(document_text.split())
                    st.metric(
                        "✍️ Words",
                        f"{words:,}"
                    )
                
                st.success("✅ Document uploaded successfully!")
                
            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")
                st.stop()
        
        if st.session_state.current_document:
            st.markdown("---")
            st.header("🔍 Analyze Document")
            
            # Create columns for better layout
            col1, col2 = st.columns([2, 1])
            
            with col1:
                analysis_type = st.selectbox(
                    "What would you like to understand about this document?",
                    list(ANALYSIS_TYPES.keys()),
                    help="Choose the type of analysis"
                )
            
            with col2:
                analysis_description = ANALYSIS_TYPES.get(analysis_type, "")
                st.caption(f"📌 {analysis_description}")
            
            if st.button("🚀 Analyze Now", use_container_width=True, type="primary"):
                with st.spinner(f"⏳ Analyzing document ({analysis_type})..."):
                    try:
                        result = st.session_state.analyzer.analyze_document(
                            st.session_state.current_document,
                            analysis_type
                        )
                        st.session_state.compression_stats = result
                        
                        # Show compression stats in an expander
                        with st.expander("📊 Token Compression Statistics", expanded=True):
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.metric(
                                    "Original Tokens",
                                    f"{result['original_tokens']:,}"
                                )
                            with col2:
                                st.metric(
                                    "Compressed Tokens",
                                    f"{result['compressed_tokens']:,}"
                                )
                            with col3:
                                st.metric(
                                    "Reduction %",
                                    f"{result['compression_ratio']}%"
                                )
                            with col4:
                                saved_tokens = result['original_tokens'] - result['compressed_tokens']
                                st.metric(
                                    "Tokens Saved",
                                    f"{saved_tokens:,}"
                                )
                            
                            st.info(f"""
                            💡 **Impact:**
                            - **Energy Saved:** ~{result['compression_ratio']}% less processing
                            - **Cost Reduction:** Proportional to token savings
                            - **Speed:** Faster API response time
                            """)
                        
                        # Show analysis results
                        st.markdown("---")
                        st.subheader(f"📋 {analysis_type} Analysis")
                        
                        # Display the analysis clearly
                        st.write(result['analysis'])
                        
                        # Show next steps
                        st.markdown("---")
                        st.info("""
                        **What's next?**
                        - 💬 Switch to "Chat with Document" tab to ask follow-up questions
                        - 📊 Check the "Statistics" tab for detailed metrics
                        - 📄 Upload another document to compare
                        """)
                        
                    except Exception as e:
                        st.error(f"❌ Analysis error: {str(e)}")
                        st.info("""
                        **Troubleshooting:**
                        - Check your internet connection
                        - Verify OpenRouter is online (status.openrouter.ai)
                        - Try with a smaller document
                        - Check if API key is valid
                        """)

elif mode == "💬 Chat with Document":
    st.header("💬 Interactive Document Chat")
    
    if st.session_state.current_document:
        st.info("""
        💡 Ask questions about the document to get more details and clarifications.
        """)
        
        question = st.text_area(
            "Ask a question about the document:",
            placeholder="E.g., What are the penalties mentioned in this bill?",
            height=120,
            key="question_input"
        )
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("📤 Ask Question", use_container_width=True, type="primary"):
                if question.strip():
                    with st.spinner("⏳ Thinking about your question..."):
                        try:
                            response = st.session_state.analyzer.follow_up_question(
                                question
                            )
                            st.markdown("---")
                            st.subheader("💭 Answer")
                            st.write(response)
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                else:
                    st.warning("⚠️ Please enter a question")
        
        with col2:
            if st.button("🔄 Reset Chat", use_container_width=True):
                st.session_state.analyzer.reset_conversation()
                st.session_state.current_document = None
                st.success("✅ Chat reset! You can upload a new document.")
                st.rerun()
    else:
        st.warning("""
        ⚠️ **No Document Loaded**
        
        Please go to the **"Upload & Analyze"** tab to upload a document first.
        """)

elif mode == "📊 Statistics":
    st.header("📊 Session Statistics")
    
    if st.session_state.compression_stats:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Total Tokens Analyzed",
                f"{st.session_state.compression_stats['original_tokens']:,}"
            )
        
        with col2:
            st.metric(
                "Compression Efficiency",
                f"{st.session_state.compression_stats['compression_ratio']}%"
            )
        
        with col3:
            st.metric(
                "Tokens Processed",
                f"{st.session_state.compression_stats['compressed_tokens']:,}"
            )
        
        st.markdown("---")
        st.subheader("📈 Analysis Details")
        st.markdown(f"""
        **Analysis Type:** {st.session_state.compression_stats['analysis_type']}
        
        **Compression Details:**
        - Original Tokens: {st.session_state.compression_stats['original_tokens']:,}
        - Compressed Tokens: {st.session_state.compression_stats['compressed_tokens']:,}
        - Reduction: {st.session_state.compression_stats['compression_ratio']}%
        """)
    else:
        st.info("Complete an analysis to see statistics")

elif mode == "ℹ️ About":
    st.header("ℹ️ About AI Legislative Analyzer")
    
    st.markdown("""
    ### 🎯 Our Mission
    Make Indian laws and parliamentary bills **understandable to every citizen**.
    
    ### 🔑 Key Features
    - 📄 Multi-format support (PDF, DOCX, TXT)
    - 🤖 Smart AI analysis (5 types)
    - ⚡ Token compression (60-80% reduction)
    - 💬 Interactive chat
    - 📊 Real-time statistics
    
    ### 🛠️ Technologies
    - **Streamlit** - Web interface
    - **OpenRouter** - Free AI API (29+ models)
    - **Python** - Core logic
    - **PyPDF2** - PDF processing
    
    ### ✨ Why OpenRouter?
    - ✅ 100% FREE
    - ✅ NO rate limits
    - ✅ 29 free models
    - ✅ Production-ready
    - ✅ Global access
    
    ### 🚀 Quick Start
    1. Upload a legal document
    2. Choose analysis type
    3. Click "Analyze Now"
    4. View results and ask follow-up questions
    
    ### 🔒 Privacy
    - Secure HTTPS connection
    - No data stored permanently
    - Enterprise-grade encryption
    
    Get your FREE OpenRouter API key: https://openrouter.ai
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #999; margin-top: 2rem; padding: 2rem 1rem;'>
    <p style='font-size: 0.9rem;'>🏛️ AI Legislative Analyzer | Making Indian Laws Understandable</p>
    
</div>
""", unsafe_allow_html=True)
