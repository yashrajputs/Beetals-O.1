# Insurance Claims Analysis System

An AI-powered insurance claims analysis system built with Streamlit that processes insurance policy PDF documents and provides automated coverage decisions with detailed justifications.

## Features

- **PDF Document Processing**: Upload and parse insurance policy documents
- **Vector Search**: Intelligent search across policy clauses using TF-IDF similarity
- **AI-Powered Analysis**: Uses Perplexity API to analyze claims against policy terms
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
git clone https://github.com/yashrajputs/filestep.git
cd filestep
```

2. Install dependencies:
```bash
pip install streamlit pymupdf requests numpy scikit-learn
```

3. Set up environment variables:
```bash
export PERPLEXITY_API_KEY="your_perplexity_api_key_here"
```

## Usage

1. Start the application:
```bash
streamlit run app.py --server.port 5000
```

2. Access the web interface at `http://localhost:5000`

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

## Technical Details

### PDF Processing
- Uses PyMuPDF for robust PDF parsing
- Implements smart section detection for policy clauses
- Extracts structured text with page references

### Search System
- TF-IDF vectorization for text similarity
- Cosine similarity matching for relevant clause retrieval
- Lightweight and efficient search without heavy ML libraries

### AI Analysis
- Leverages Perplexity's Sonar model for real-time analysis
- Structured prompts for consistent JSON responses
- Context-aware decision making based on policy content

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