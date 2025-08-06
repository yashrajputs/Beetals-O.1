import streamlit as st
import os
import json
import tempfile
from utils.pdf_processor import extract_structured_sections, is_valid_pdf
from utils.vector_search import create_vector_index, get_top_similar_clauses
from utils.ai_analyzer import analyze_claim_with_ai

# Page configuration
st.set_page_config(
    page_title="Insurance Claims Analysis System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'processed_document' not in st.session_state:
    st.session_state.processed_document = None
if 'vector_index' not in st.session_state:
    st.session_state.vector_index = None
if 'structured_clauses' not in st.session_state:
    st.session_state.structured_clauses = None
if 'model' not in st.session_state:
    st.session_state.model = None

def main():
    st.title("🏥 Insurance Claims Analysis System")
    st.markdown("---")
    
    # API Key check
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        st.error("⚠️ PERPLEXITY_API_KEY environment variable not found. Please set your API key.")
        st.stop()
    
    # Sidebar for document upload
    with st.sidebar:
        st.header("📄 Document Upload")
        uploaded_file = st.file_uploader(
            "Upload Insurance Policy PDF",
            type=['pdf'],
            help="Upload a PDF file containing insurance policy documents"
        )
        
        if uploaded_file is not None:
            if st.button("🔄 Process Document", type="primary"):
                process_document(uploaded_file)
    
    # Main content area
    if st.session_state.processed_document is None:
        st.info("👆 Please upload an insurance policy PDF document to get started.")
        st.markdown("""
        ### How to use this system:
        1. **Upload** your insurance policy PDF using the sidebar
        2. **Process** the document to extract policy clauses
        3. **Enter** your claim query in natural language
        4. **Get** AI-powered coverage analysis with justification
        """)
    else:
        display_analysis_interface()

def process_document(uploaded_file):
    """Process the uploaded PDF document"""
    with st.spinner("🔄 Processing document..."):
        try:
            # Save uploaded file to temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            # Validate PDF
            if not is_valid_pdf(tmp_file_path):
                st.error("❌ Invalid PDF file. Please upload a valid PDF document.")
                os.unlink(tmp_file_path)
                return
            
            # Extract structured sections
            progress_bar = st.progress(0, "Extracting document sections...")
            structured_clauses = extract_structured_sections(tmp_file_path)
            progress_bar.progress(50, "Processing clauses...")
            
            # Filter out short clauses
            structured_clauses = [clause for clause in structured_clauses if len(clause['text']) > 50]
            
            if not structured_clauses:
                st.error("❌ No valid clauses found in the document. Please check the PDF content.")
                os.unlink(tmp_file_path)
                return
            
            progress_bar.progress(75, "Creating vector index...")
            
            # Create vector index
            vector_index, model = create_vector_index(structured_clauses)
            
            progress_bar.progress(100, "Document processed successfully!")
            
            # Store in session state
            st.session_state.processed_document = uploaded_file.name
            st.session_state.vector_index = vector_index
            st.session_state.structured_clauses = structured_clauses
            st.session_state.model = model
            
            # Clean up temporary file
            os.unlink(tmp_file_path)
            
            st.success(f"✅ Successfully processed {len(structured_clauses)} policy clauses from '{uploaded_file.name}'")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error processing document: {str(e)}")
            # Clean up temporary file if it exists
            try:
                if 'tmp_file_path' in locals() and os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
            except:
                pass

def display_analysis_interface():
    """Display the main analysis interface"""
    st.header("🔍 Claims Analysis")
    
    # Document info
    st.success(f"📄 Document loaded: {st.session_state.processed_document}")
    st.info(f"📊 {len(st.session_state.structured_clauses)} policy clauses indexed")
    
    # Query input
    st.subheader("Enter Your Claim Query")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query = st.text_area(
            "Describe your insurance claim:",
            placeholder="Example: 50M, used air ambulance, distance traveled 300 km, seeking 100% reimbursement",
            height=100
        )
    
    with col2:
        st.markdown("### Quick Examples")
        example_queries = [
            "50M, used air ambulance, distance traveled 300 km, seeking 100% reimbursement",
            "35F, pre-existing diabetes, hospitalization for 5 days",
            "28M, outpatient surgery, day care procedure claim",
            "45F, maternity expenses, normal delivery claim"
        ]
        
        for i, example in enumerate(example_queries):
            if st.button(f"Example {i+1}", key=f"example_{i}", help=example):
                st.session_state.example_query = example
                st.rerun()
    
    # Use example query if selected
    if hasattr(st.session_state, 'example_query'):
        query = st.session_state.example_query
        delattr(st.session_state, 'example_query')
    
    # Analysis button
    if st.button("🔍 Analyze Claim", type="primary", disabled=not query.strip()):
        analyze_claim(query)

def analyze_claim(query):
    """Analyze the insurance claim"""
    with st.spinner("🔍 Analyzing your claim..."):
        try:
            # Get relevant clauses
            progress_bar = st.progress(0, "Finding relevant clauses...")
            relevant_clauses = get_top_similar_clauses(
                query=query,
                indexed_data=st.session_state.structured_clauses,
                index=st.session_state.vector_index,
                model=st.session_state.model,
                k=5
            )
            
            progress_bar.progress(50, "Getting AI analysis...")
            
            # Get AI analysis
            analysis_result = analyze_claim_with_ai(query, relevant_clauses)
            
            progress_bar.progress(100, "Analysis complete!")
            
            # Display results
            display_analysis_results(query, relevant_clauses, analysis_result)
            
        except Exception as e:
            st.error(f"❌ Error analyzing claim: {str(e)}")

def display_analysis_results(query, relevant_clauses, analysis_result):
    """Display the analysis results"""
    st.markdown("---")
    st.header("📋 Analysis Results")
    
    # Query recap
    st.subheader("🔍 Your Query")
    st.info(query)
    
    # AI Analysis
    st.subheader("🤖 AI Coverage Analysis")
    
    if analysis_result:
        try:
            # Try to parse JSON response
            if isinstance(analysis_result, str):
                # Try to extract JSON from the response
                json_start = analysis_result.find('{')
                json_end = analysis_result.rfind('}') + 1
                if json_start != -1 and json_end != 0:
                    json_str = analysis_result[json_start:json_end]
                    result = json.loads(json_str)
                else:
                    raise ValueError("No JSON found in response")
            else:
                result = analysis_result
            
            # Display decision
            decision = result.get('decision', 'Unknown')
            amount = result.get('amount', 'Not specified')
            justification = result.get('justification', 'No justification provided')
            
            # Decision display
            if decision.lower() == 'yes':
                st.success(f"✅ **Coverage Decision:** {decision}")
            elif decision.lower() == 'no':
                st.error(f"❌ **Coverage Decision:** {decision}")
            else:
                st.warning(f"⚠️ **Coverage Decision:** {decision}")
            
            # Amount display
            if amount and amount != 'Not specified':
                st.info(f"💰 **Amount:** {amount}")
            
            # Justification
            st.markdown("**📝 Justification:**")
            st.write(justification)
            
        except (json.JSONDecodeError, ValueError):
            # Fallback to raw response
            st.write("**AI Response:**")
            st.write(analysis_result)
    else:
        st.error("❌ No analysis result received")
    
    # Relevant clauses
    st.subheader("📄 Relevant Policy Clauses")
    
    for i, clause in enumerate(relevant_clauses, 1):
        with st.expander(f"Clause {i}: {clause['title']} (Page {clause['page_number']})"):
            st.write(clause['text'])
    
    # Reset button
    if st.button("🔄 New Analysis"):
        st.rerun()

if __name__ == "__main__":
    main()
