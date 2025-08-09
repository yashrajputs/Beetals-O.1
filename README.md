# FileStarter - Insurance Claims Analysis System

An AI-powered insurance claims analysis system built with Streamlit that processes insurance policy PDF documents and provides automated coverage decisions with detailed justifications.

🚀 **[Live Demo on Streamlit Cloud](https://share.streamlit.io)** (Deploy using instructions below)

## Features

- **PDF Document Processing**: Upload and parse insurance policy documents
- **Vector Search**: Intelligent search across policy clauses using ChromaDB
- **AI-Powered Analysis**: Uses Perplexity API to analyze claims against policy terms
- **Session State Persistence**: Auto-restore documents from database after refresh
- **Database Storage**: SQLite + ChromaDB for persistent document storage
- **Structured JSON Output**: Returns decisions with Yes/No coverage determination and detailed policy statements
- **Multiple Query Support**: Analyze multiple claims simultaneously
- **Real-time Processing**: Interactive web interface with live results

## System Architecture

### Frontend
- **Streamlit**: Interactive web application framework
- **Session State Management**: Maintains processed documents and search indices
- **File Upload Interface**: Drag-and-drop PDF upload with progress tracking

### Backend
- **Modular Design**: Separated into three core utilities:
  - `pdf_processor.py`: PDF parsing and text extraction
  - `vector_search.py`: TF-IDF-based semantic search
  - `ai_analyzer.py`: Perplexity API integration for claim analysis

### AI Integration
- **Perplexity API**: Real-time search and analysis capabilities
- **Structured Responses**: JSON-formatted outputs with coverage decisions
- **Context-Aware**: Uses relevant policy clauses for accurate analysis

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yashrajputs/Beetals-O.1.git
cd Beetals-O.1
```

2. Install dependencies:
```bash
pip install streamlit pymupdf requests numpy scikit-learn
```

3. Set up environment variables:
```bash
export PERPLEXITY_API_KEY="your_perplexity_api_key_here"
```

## 🚀 Deploy to Streamlit Cloud

**Quick Deploy (Recommended):**

1. **Go to**: https://share.streamlit.io/
2. **Sign in** with your GitHub account  
3. **Click "New app"**
4. **Configure**:
   - Repository: `yashrajputs/Beetals-O.1`
   - Branch: `main`
   - Main file path: `app.py`
   - App URL: Choose your custom URL
5. **Add secrets** in Advanced settings:
   ```toml
   PERPLEXITY_API_KEY = "your_actual_api_key_here"
   ```
6. **Click "Deploy!"**

✅ **Your app will be live at**: `https://your-chosen-url.streamlit.app`

## Local Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Access the web interface at `http://localhost:8501`

3. Upload an insurance policy PDF document

4. Enter claim queries to analyze coverage

5. View structured JSON results with decisions and policy justifications

## API Configuration

The system requires a Perplexity API key for AI analysis. Get your key from:
1. Visit [Perplexity AI](https://www.perplexity.ai/)
2. Create an account or sign in
3. Generate an API key from your account settings
4. Set the `PERPLEXITY_API_KEY` environment variable

## Output Format

The system returns structured JSON responses:

```json
{
  "claim_id": 1,
  "query": "Is dental treatment covered?",
  "decision": "Yes/No",
  "answers": [
    "Dental treatment is covered up to ₹50,000 per year",
    "Coverage includes routine checkups and major procedures",
    "Pre-existing dental conditions have a 2-year waiting period",
    "Emergency dental treatment is covered immediately"
  ],
  "relevant_clauses": [...]
}
```

## Project Structure

```
├── app.py                 # Main Streamlit application
├── utils/
│   ├── pdf_processor.py   # PDF parsing and text extraction
│   ├── vector_search.py   # TF-IDF similarity search
│   └── ai_analyzer.py     # Perplexity API integration
├── .streamlit/
│   └── config.toml        # Streamlit configuration
├── requirements.txt       # Python dependencies
└── README.md             # Project documentation
```

## Dependencies

- **streamlit**: Web application framework
- **pymupdf (fitz)**: PDF processing and text extraction
- **requests**: HTTP client for API calls
- **numpy**: Numerical computing
- **scikit-learn**: Machine learning utilities for TF-IDF

## 📊 Data Storage & Session Management

### Storage Architecture
- **SQLite Database**: Persistent storage for documents and clauses
- **ChromaDB**: Vector embeddings for semantic search (with fallback)
- **Session State**: In-memory UI state (auto-restored from database)
- **File Processing**: Temporary upload processing with permanent storage

### Session Persistence
- ✅ **Documents**: Auto-restored from database on refresh
- ✅ **Search Indices**: Persistent vector storage
- ✅ **User Data**: Survives browser refresh and server restart
- ❌ **UI State**: Temporary (forms, selections) - resets on refresh

### Data Storage Analysis
Run the included storage analysis tool:
```bash
python check_data_storage.py
```

## Technical Details

### PDF Processing
- Uses PyMuPDF for robust PDF parsing with fallback support
- Implements smart section detection for policy clauses
- Extracts structured text with page references
- Mock implementation available for deployment environments

### Search System
- ChromaDB for advanced vector similarity (when available)
- TF-IDF fallback for text similarity matching
- Cosine similarity matching for relevant clause retrieval
- Lightweight and efficient search without heavy ML dependencies

### AI Analysis
- Leverages Perplexity's Sonar model for real-time analysis
- Structured prompts for consistent JSON responses
- Context-aware decision making based on policy content
- Graceful error handling and fallback mechanisms

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please open an issue on the GitHub repository.