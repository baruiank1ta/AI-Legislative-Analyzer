# 🏛️ AI Legislative Analyzer - Quick Reference Guide

## 🚀 Quick Start (5 Minutes)

### 1. Download & Setup
```bash
# Windows - Double click setup.bat
# Or run these commands:
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

```bash
# macOS/Linux
chmod +x setup.sh
./setup.sh
# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Add Your API Key
1. Get key from https://console.anthropic.com
2. Create `.env` file (or rename `.env.example`)
3. Add: `ANTHROPIC_API_KEY=your_key_here`

### 3. Run the App
```bash
streamlit run main.py
```

Open browser → http://localhost:8501

---

## 📁 Project Structure

```
ai-legislative-analyzer/
├── main.py                 # Main Streamlit app (run this!)
├── utils.py                # Token compression & API logic
├── config.py               # Settings and configuration
├── requirements.txt        # Python dependencies
├── .env                    # Your API key (CREATE THIS!)
├── .env.example            # Template for .env
├── setup.sh                # Auto-setup script (Mac/Linux)
├── setup.bat               # Auto-setup script (Windows)
├── uploaded_documents/     # Where uploads are saved
└── README files            # Documentation
```

---

## 🎯 How to Use the App

### Upload & Analyze Tab
1. Click file upload button
2. Select PDF, DOCX, or TXT file
3. See document statistics
4. Choose analysis type:
   - **Summary** - Understand bill simply
   - **Key Changes** - What's new
   - **Impact** - Who it affects
   - **Comparison** - vs existing laws
   - **Implementation** - How it works
5. Click "Analyze Now"
6. View results + token compression stats

### Chat with Document Tab
1. Upload a document first
2. Ask specific questions
3. Get detailed answers
4. Reset conversation anytime

### Statistics Tab
- See token compression metrics
- Understand energy savings
- View cost reduction

### About Tab
- Learn how compression works
- See technologies used
- Get usage examples

---

## 💡 Understanding Token Compression

### What Are Tokens?
- Small units of text
- Roughly: 1 token = 4 characters
- Larger documents = more tokens
- More tokens = higher cost & energy

### What Does Compression Do?
- Removes legal boilerplate (preambles, disclaimers)
- Keeps important information
- Reduces tokens by 60-80%
- Same analysis quality, lower cost!

### Example
```
Original: "The Government of India, in exercise of the 
powers conferred by Article 123 of the Constitution of India, 
hereby declares that the following rules shall apply..."
(~100 tokens)

Compressed: "GoI declares (Article 123) - New rules apply"
(~15 tokens)

Savings: 85% fewer tokens! ⚡
```

---

## 🔧 Configuration Options

Edit `config.py` to customize:

```python
# Use different Claude model
MODEL = "claude-3-5-sonnet-20241022"

# Change token limits
MAX_TOKENS = 4000  # Increase for longer responses

# Adjust compression
COMPRESSION_RATIO = 0.3  # Keep 30% of tokens

# Add custom analysis types
ANALYSIS_TYPES = {
    'Your Type': 'Your prompt here',
    ...
}
```

---

## ⚠️ Common Issues & Fixes

### ❌ "API Key not found"
**Fix:**
1. Create `.env` file in project root
2. Add your actual key: `ANTHROPIC_API_KEY=sk-ant-...`
3. Restart the app

### ❌ "PDF not reading"
**Fix:**
1. Try a different PDF
2. Ensure it's not corrupted
3. Try converting scanned PDF to text first

### ❌ "Module not found" errors
**Fix:**
```bash
# Make sure venv is activated
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate.bat # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### ❌ "Slow analysis"
**This is normal!** Large documents take time to compress.
- Smaller docs = faster analysis
- Be patient with 100k+ token documents

### ❌ "Port already in use"
**Fix:**
```bash
streamlit run main.py --server.port 8502
```

---

## 📚 File Format Support

### PDF
- ✅ Digital PDFs (searchable)
- ✅ Scanned PDFs (with good OCR)
- ❌ Very low quality scans
- Max: 50 MB

### DOCX (Word)
- ✅ Modern Word documents
- ✅ Tables and formatting
- ✅ Tracked changes
- Max: 50 MB

### TXT (Plain Text)
- ✅ Any plain text format
- ✅ Simplest format
- ✅ Works perfectly
- Max: 50 MB

---

## 🤖 How the AI Works

### Step 1: Document Upload
```
Your file → App reads content
```

### Step 2: Token Compression
```
Full text → Remove boilerplate
        → Extract key sentences
        → Remove redundancy
        → Compressed text (60-80% smaller!)
```

### Step 3: Send to Claude
```
Compressed text + Your question → Claude API
```

### Step 4: Get Results
```
Claude analyzes → Returns answer → You read analysis
```

---

## 💾 Data Storage

### What's Kept?
- ✅ Your conversation history (during session)
- ✅ Uploaded files (in `uploaded_documents/` folder)

### What's Deleted?
- ✅ Conversation resets when you close app
- ✅ Consider clearing `uploaded_documents/` folder regularly

### Privacy
- 📤 Files sent to Claude API (secure HTTPS)
- 🔒 Not stored permanently by Anthropic
- 🛡️ Enterprise-grade security
- ✅ See: https://www.anthropic.com/privacy

---

## 📊 Token Compression Algorithm

### Step 1: Cleaning
- Remove extra spaces
- Remove page numbers
- Remove headers/footers

### Step 2: Boilerplate Removal
Identifies and removes:
- Standard legal preambles
- "Whereas" sections
- Generic disclaimers
- Repetitive sections

### Step 3: Keyword Extraction
Finds sentences with legal keywords:
- "shall", "must", "require"
- "prohibit", "amend", "repeal"
- "penalty", "fine", "offense"
- "section", "rule", "article"

### Step 4: Redundancy Removal
- Removes duplicate sentences
- Removes near-duplicate information
- Keeps unique content only

### Result
- 60-80% token reduction
- All important info preserved
- Faster processing
- Lower costs

---

## 🚀 Advanced Usage

### Multiple Documents
- Upload different bills
- Compare their analyses
- Ask comparative questions

### Batch Processing
```python
from utils import DocumentProcessor, LegislativeAnalyzer

analyzer = LegislativeAnalyzer()

for pdf_file in pdf_files:
    text = DocumentProcessor.extract_text(pdf_file, 'pdf')
    result = analyzer.analyze_document(text, 'Summary')
    print(result['analysis'])
```

### Custom Prompts
Edit `config.py`:
```python
ANALYSIS_TYPES = {
    'My Custom Type': 'Your custom prompt here'
}
```

---

## 🔗 Important Links

- **API Key:** https://console.anthropic.com
- **Claude Docs:** https://docs.claude.com
- **Streamlit Docs:** https://docs.streamlit.io
- **Privacy Policy:** https://www.anthropic.com/privacy
- **Contact:** support@anthropic.com

---

## 📈 Performance Tips

1. **Use smaller documents first**
   - Test with 5-10 page bills first
   - Graduate to larger documents

2. **Clean PDFs work better**
   - Searchable PDFs > Scanned PDFs
   - Good OCR > Bad OCR

3. **Ask specific questions**
   - "What are penalties?" > "Tell me about this"
   - One question per chat > Multiple questions

4. **Use appropriate analysis types**
   - Summary for overview
   - Impact for consequences
   - Implementation for practical details

---

## 🎓 Learning Resources

### Understanding Indian Legislation
- Start with simple bills
- Use Summary analysis first
- Then ask follow-up questions
- Read about related bills

### Using Token Compression
- Watch the reduction percentage
- Understand what was compressed
- Learn from statistics

### Improving Prompts
- Be specific
- Ask one thing at a time
- Reference sections/clauses
- Request examples

---

## 🆘 Getting Help

### Check These First
1. Is your API key correct?
2. Is Python 3.9+ installed?
3. Is virtual environment activated?
4. Are all dependencies installed?

### Common Solutions
```bash
# Activate virtual environment
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate.bat # Windows

# Check Python version
python --version

# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Test API key
echo $ANTHROPIC_API_KEY  # Mac/Linux
echo %ANTHROPIC_API_KEY% # Windows
```

### Still Stuck?
- Check error messages carefully
- Review documentation at setup
- Check file locations
- Ensure all files are present

---

## 🎯 Example Workflow

### Scenario: Understand New Tax Law

1. **Download** the tax bill PDF from government website
2. **Upload** to the app
3. **Select** "Impact Assessment" analysis
4. **Read** simplified explanation
5. **Ask** "Who qualifies for exemptions?"
6. **Ask** "What are the penalties?"
7. **Screenshot** important parts
8. **Share** with friends/family

Total time: ~5-10 minutes
Traditional reading: ~30-60 minutes

---

## 🏆 Best Practices

### Do ✅
- Read the summaries first
- Ask specific follow-up questions
- Try different analysis types
- Read the token stats
- Check compression ratio

### Don't ❌
- Upload unrelated documents
- Ask extremely long multi-part questions
- Expect perfect legal accuracy
- Share sensitive information
- Modify code without testing

---

## 🔐 Security Checklist

- [ ] API key in `.env` (not in code)
- [ ] `.env` in `.gitignore` (if using Git)
- [ ] Don't share `.env` file
- [ ] Delete old uploaded documents
- [ ] Use on secure network
- [ ] Keep Python updated

---

## 📞 Support Resources

**Inside App:**
- Each tab has "?" expandable sections
- Error messages are descriptive
- Sidebar has helpful tips

**Online:**
- Claude docs: docs.claude.com
- Streamlit docs: docs.streamlit.io
- Anthropic support: support@anthropic.com

---

**Happy analyzing! Make Indian laws accessible to everyone! 🇮🇳**
