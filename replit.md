# Insurance Claims Analysis System

## Overview

This is an AI-powered insurance claims analysis system built with Streamlit that helps analyze insurance policies and process claims. The system extracts structured information from insurance policy PDFs, creates searchable vector embeddings, and uses AI to analyze claims against policy terms. It provides automated claim decisions with justifications based on relevant policy clauses.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Streamlit Web Framework**: Provides the interactive web interface with file upload capabilities, document processing workflow, and results display
- **Session State Management**: Maintains processed documents, vector indices, and structured clauses across user interactions
- **Sidebar Navigation**: Dedicated document upload section with processing controls

### Backend Architecture
- **Modular Utility Structure**: Core functionality split into three main modules:
  - `pdf_processor.py`: Handles PDF parsing, text extraction, and clause structuring
  - `vector_search.py`: Manages semantic search using sentence transformers and FAISS indexing
  - `ai_analyzer.py`: Interfaces with Perplexity AI for claim analysis and decision generation

### Document Processing Pipeline
- **PDF Text Extraction**: Uses PyMuPDF/fitz for robust PDF parsing and text extraction
- **Smart Section Detection**: Implements heuristic-based title recognition to identify policy sections and clauses
- **Structured Data Creation**: Converts raw PDF text into structured clauses with titles, content, and page references

### Search and Retrieval System
- **Semantic Vector Search**: Uses BAAI/bge-base-en-v1.5 sentence transformer for generating text embeddings
- **FAISS Vector Database**: Provides efficient similarity search across policy clauses
- **Top-K Retrieval**: Returns most relevant policy sections for any given claim query

### AI Analysis Engine
- **Perplexity AI Integration**: Leverages external AI API for intelligent claim analysis
- **Structured Decision Output**: Returns JSON-formatted decisions with coverage determination, amounts, and detailed justifications
- **Context-Aware Analysis**: Uses retrieved policy clauses as context for accurate claim evaluation

### Data Flow Architecture
1. PDF upload and validation
2. Text extraction and section identification
3. Vector embedding generation and indexing
4. Query processing and similarity search
5. AI-powered analysis with structured output

## External Dependencies

### Third-Party APIs
- **Perplexity AI API**: Primary AI service for claim analysis and decision generation (requires PERPLEXITY_API_KEY environment variable)

### Machine Learning Libraries
- **Sentence Transformers**: BAAI/bge-base-en-v1.5 model for semantic text embeddings
- **FAISS**: Facebook's library for efficient similarity search and clustering of dense vectors
- **NumPy**: Numerical computing for vector operations

### Document Processing
- **PyMuPDF (fitz)**: PDF parsing and text extraction library
- **Regular Expressions**: Pattern matching for title detection and text cleanup

### Web Framework
- **Streamlit**: Complete web application framework for the user interface

### Environment Configuration
- **OS Environment Variables**: Configuration management for API keys and system settings
- **Tempfile**: Temporary file handling for uploaded documents
- **JSON**: Data serialization for API communication and structured outputs