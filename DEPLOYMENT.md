# Deployment Guide

## GitHub Setup

1. **Initialize Repository** (if not already done):
```bash
git init
git add .
git commit -m "Initial commit: Insurance Claims Analysis System"
```

2. **Add Remote Repository**:
```bash
git remote add origin https://github.com/yashrajputs/filestep.git
git branch -M main
git push -u origin main
```

## Local Development

1. **Clone and Setup**:
```bash
git clone https://github.com/yashrajputs/filestep.git
cd filestep
pip install -r dependencies.txt
```

2. **Environment Configuration**:
```bash
export PERPLEXITY_API_KEY="your_api_key_here"
```

3. **Run Application**:
```bash
streamlit run app.py --server.port 5000
```

## Replit Deployment

1. **Import from GitHub**:
   - Go to Replit.com
   - Click "Create Repl"
   - Choose "Import from GitHub"
   - Enter repository URL: https://github.com/yashrajputs/filestep

2. **Configure Secrets**:
   - Add `PERPLEXITY_API_KEY` in Replit Secrets
   - The system will automatically use environment variables

3. **Run Configuration**:
   - Replit will auto-detect the Streamlit app
   - Or manually configure: `streamlit run app.py --server.port 5000`

## Environment Variables

Required environment variables:
- `PERPLEXITY_API_KEY`: Your Perplexity AI API key

Optional configurations:
- `STREAMLIT_SERVER_PORT`: Server port (default: 5000)
- `STREAMLIT_SERVER_ADDRESS`: Server address (default: 0.0.0.0)

## File Structure for GitHub

```
filestep/
├── app.py                 # Main application
├── utils/
│   ├── __init__.py       # Package initializer
│   ├── pdf_processor.py   # PDF processing utilities
│   ├── vector_search.py   # Search functionality
│   └── ai_analyzer.py     # AI integration
├── .streamlit/
│   └── config.toml        # Streamlit configuration
├── README.md             # Project documentation
├── dependencies.txt      # Python dependencies
├── DEPLOYMENT.md         # This file
├── .gitignore           # Git ignore patterns
└── replit.md            # Replit-specific documentation
```

## Production Considerations

1. **Security**:
   - Never commit API keys to version control
   - Use environment variables or secure secret management
   - Review .gitignore to exclude sensitive files

2. **Performance**:
   - Consider upgrading to Perplexity Pro API for higher limits
   - Implement caching for frequently analyzed documents
   - Add request rate limiting if needed

3. **Monitoring**:
   - Add logging for API requests and errors
   - Monitor usage costs for Perplexity API
   - Set up error tracking and alerts

## Troubleshooting

**Common Issues**:

1. **API Authentication Error (401)**:
   - Verify PERPLEXITY_API_KEY is set correctly
   - Check if API key is valid and not expired

2. **Module Import Errors**:
   - Ensure all dependencies are installed
   - Check Python version compatibility (3.8+)

3. **PDF Processing Issues**:
   - Verify PyMuPDF installation
   - Check PDF file format and permissions

4. **Streamlit Startup Issues**:
   - Ensure port 5000 is available
   - Check .streamlit/config.toml configuration