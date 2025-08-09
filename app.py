import streamlit as st
import os
import json
import tempfile
from utils.pdf_processor import extract_structured_sections, is_valid_pdf
from utils.vector_search import create_vector_index, get_top_similar_clauses, create_vector_index_with_db, get_top_similar_clauses_from_db
from utils.ai_analyzer import analyze_claim_with_ai
from utils.database_manager import DatabaseManager

# Page configuration
# Streamlit page configuration
try:
    st.set_page_config(
        page_title="Insurance Claims Analysis System",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
except Exception:
    pass  # Handle case where page config is already set

# Initialize session state
if 'processed_document' not in st.session_state:
    st.session_state.processed_document = None
if 'vector_index' not in st.session_state:
    st.session_state.vector_index = None
if 'structured_clauses' not in st.session_state:
    st.session_state.structured_clauses = None
if 'model' not in st.session_state:
    st.session_state.model = None
if 'document_id' not in st.session_state:
    st.session_state.document_id = None
if 'db_manager' not in st.session_state:
    try:
        st.session_state.db_manager = DatabaseManager()
    except Exception as e:
        st.error(f"Failed to initialize database: {str(e)}")
        st.stop()

# Auto-restore last processed document if session state is empty
if ('processed_document' not in st.session_state or 
    st.session_state.processed_document is None) and st.session_state.db_manager:
    try:
        # Get the most recently processed document
        documents = st.session_state.db_manager.get_all_documents()
        if documents:
            latest_doc = documents[0]  # Already sorted by upload_date DESC
            load_document_from_db_silent(latest_doc['id'])
    except Exception:
        pass  # Silent fail - user can manually load if needed

def main():
    st.title("🏥 Insurance Claims Analysis System")
    st.markdown("---")
    
    # API Key check
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        # Check Streamlit secrets as fallback
        try:
            api_key = st.secrets["PERPLEXITY_API_KEY"]
        except (KeyError, FileNotFoundError):
            st.error("⚠️ PERPLEXITY_API_KEY not found. Please set your API key in Streamlit Cloud secrets.")
            st.markdown("""
            **For Streamlit Cloud deployment:**
            1. Go to your app settings
            2. Click on "Secrets" in the sidebar
            3. Add: `PERPLEXITY_API_KEY = "your_key_here"`
            """)
            st.stop()
    
    # Sidebar for document upload and management
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
        
        st.markdown("---")
        
        # Database management section
        st.header("💾 Database Management")
        
        # Display database stats
        if st.session_state.db_manager:
            stats = st.session_state.db_manager.get_database_stats()
            st.metric("Documents Stored", stats['document_count'])
            st.metric("Total Clauses", stats['clause_count'])
            
            # Show database size in KB/MB
            total_size = stats['total_file_size']
            if total_size > 1024 * 1024:
                size_str = f"{total_size / (1024 * 1024):.1f} MB"
            elif total_size > 1024:
                size_str = f"{total_size / 1024:.1f} KB"
            else:
                size_str = f"{total_size} bytes"
            st.metric("Storage Used", size_str)
            
            # List stored documents
            if stats['document_count'] > 0:
                st.subheader("📚 Stored Documents")
                documents = st.session_state.db_manager.get_all_documents()
                
                for doc in documents:
                    with st.expander(f"📄 {doc['filename']}"):
                        st.text(f"Uploaded: {doc['upload_date']}")
                        st.text(f"Clauses: {doc['total_clauses']}")
                        st.text(f"File Size: {doc['file_size']} bytes")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"Load", key=f"load_{doc['id']}"):
                                load_document_from_db(doc['id'])
                        with col2:
                            if st.button(f"Delete", key=f"delete_{doc['id']}"):
                                if st.session_state.db_manager.delete_document(doc['id']):
                                    st.success(f"Deleted {doc['filename']}")
                                    st.rerun()
        
        st.markdown("---")
        
        # Help section
        st.header("❓ Help")
        st.markdown("""
        **Database Features:**
        - ✅ Persistent storage
        - ✅ Vector search with ChromaDB
        - ✅ Duplicate detection
        - ✅ Fast loading of processed documents
        - ✅ Document management
        """)
    
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
        # Show session status if document was auto-restored
        if 'auto_restored' not in st.session_state:
            st.session_state.auto_restored = True
            st.info("🔄 Session restored from database! Your previously processed document is ready.")
        display_analysis_interface()

def process_document(uploaded_file):
    """Process the uploaded PDF document using database storage"""
    with st.spinner("🔄 Processing document..."):
        try:
            file_content = uploaded_file.getvalue()
            db_manager = st.session_state.db_manager
            
            # Check if document already exists
            progress_bar = st.progress(0, "Checking if document exists...")
            existing_doc_id = db_manager.document_exists(uploaded_file.name, file_content)
            
            if existing_doc_id:
                st.info("📄 Document already processed! Loading from database...")
                # Load existing document
                progress_bar.progress(50, "Loading existing document...")
                document_info = db_manager.get_document_by_id(existing_doc_id)
                structured_clauses = db_manager.get_clauses_by_document_id(existing_doc_id)
                
                progress_bar.progress(100, "Document loaded successfully!")
                
                # Update session state
                st.session_state.processed_document = uploaded_file.name
                st.session_state.document_id = existing_doc_id
                st.session_state.structured_clauses = structured_clauses
                st.session_state.vector_index = {'type': 'chromadb', 'document_id': existing_doc_id}
                st.session_state.model = None
                
                st.success(f"✅ Loaded existing document with {len(structured_clauses)} policy clauses from '{uploaded_file.name}'")
                st.rerun()
                return
            
            # Process new document
            progress_bar.progress(10, "Validating PDF...")
            
            # Save uploaded file to temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(file_content)
                tmp_file_path = tmp_file.name
            
            # Validate PDF
            if not is_valid_pdf(tmp_file_path):
                st.error("❌ Invalid PDF file. Please upload a valid PDF document.")
                os.unlink(tmp_file_path)
                return
            
            # Extract structured sections
            progress_bar.progress(25, "Extracting document sections...")
            structured_clauses = extract_structured_sections(tmp_file_path)
            
            # Filter out short clauses
            structured_clauses = [clause for clause in structured_clauses if len(clause['text']) > 50]
            
            if not structured_clauses:
                st.error("❌ No valid clauses found in the document. Please check the PDF content.")
                os.unlink(tmp_file_path)
                return
            
            progress_bar.progress(50, "Storing document in database...")
            
            # Store document in database
            document_id = db_manager.store_document(
                filename=uploaded_file.name,
                file_content=file_content,
                structured_clauses=structured_clauses
            )
            
            progress_bar.progress(75, "Creating vector index...")
            
            # Create and store vector index
            collection_name = create_vector_index_with_db(
                structured_clauses=structured_clauses,
                db_manager=db_manager,
                document_id=document_id
            )
            
            progress_bar.progress(100, "Document processed successfully!")
            
            # Update session state
            st.session_state.processed_document = uploaded_file.name
            st.session_state.document_id = document_id
            st.session_state.structured_clauses = structured_clauses
            st.session_state.vector_index = {'type': 'chromadb', 'document_id': document_id}
            st.session_state.model = None
            
            # Clean up temporary file
            os.unlink(tmp_file_path)
            
            st.success(f"✅ Successfully processed and stored {len(structured_clauses)} policy clauses from '{uploaded_file.name}'")
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
    
    # Query input section
    st.subheader("Enter Your Claim Queries")
    
    # Initialize query list in session state
    if 'query_list' not in st.session_state:
        st.session_state.query_list = [""]
    
    # Multiple query input
    st.markdown("**Add multiple queries (one per line):**")
    queries_text = st.text_area(
        "Describe your insurance claims:",
        value="\n".join(st.session_state.query_list) if st.session_state.query_list[0] else "",
        placeholder="Example:\n50M, used air ambulance, distance traveled 300 km, seeking 100% reimbursement\n35F, pre-existing diabetes, hospitalization for 5 days\n28M, outpatient surgery, day care procedure claim",
        height=150,
        help="Enter one claim per line. You can analyze multiple claims at once."
    )
    
    # Parse queries
    if queries_text.strip():
        query_list = [q.strip() for q in queries_text.split('\n') if q.strip()]
        st.session_state.query_list = query_list
    else:
        st.session_state.query_list = [""]
    
    # Quick examples section
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.markdown("### Quick Examples")
        example_queries = [
            "50M, used air ambulance, distance traveled 300 km, seeking 100% reimbursement",
            "35F, pre-existing diabetes, hospitalization for 5 days", 
            "28M, outpatient surgery, day care procedure claim",
            "45F, maternity expenses, normal delivery claim"
        ]
        
        if st.button("Load All Examples", key="load_examples"):
            st.session_state.query_list = example_queries
            st.rerun()
        
        for i, example in enumerate(example_queries):
            if st.button(f"Add Example {i+1}", key=f"example_{i}", help=example):
                if st.session_state.query_list == [""]:
                    st.session_state.query_list = [example]
                else:
                    st.session_state.query_list.append(example)
                st.rerun()
    
    with col1:
        # Analysis button
        valid_queries = [q for q in st.session_state.query_list if q.strip()]
        if st.button("🔍 Analyze Claims", type="primary", disabled=not valid_queries):
            analyze_multiple_claims(valid_queries)

def analyze_claim(query):
    """Analyze a single insurance claim"""
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

def analyze_multiple_claims(queries):
    """Analyze multiple insurance claims using database"""
    results = []
    
    with st.spinner(f"🔍 Analyzing {len(queries)} claims..."):
        try:
            db_manager = st.session_state.db_manager
            document_id = st.session_state.document_id
            
            for i, query in enumerate(queries):
                # Update progress
                progress = (i + 1) / len(queries)
                st.progress(progress, f"Analyzing claim {i+1} of {len(queries)}")
                
                # Get relevant clauses using database vector search
                if document_id and st.session_state.vector_index.get('type') == 'chromadb':
                    relevant_clauses = get_top_similar_clauses_from_db(
                        query=query,
                        db_manager=db_manager,
                        document_id=document_id,
                        k=5
                    )
                else:
                    # Fallback to legacy method
                    relevant_clauses = get_top_similar_clauses(
                        query=query,
                        indexed_data=st.session_state.structured_clauses,
                        index=st.session_state.vector_index,
                        model=st.session_state.model,
                        k=5
                    )
                
                # Get AI analysis
                analysis_result = analyze_claim_with_ai(query, relevant_clauses)
                
                # Store result
                results.append({
                    "query": query,
                    "relevant_clauses": relevant_clauses,
                    "analysis": analysis_result
                })
            
            # Display results in JSON format
            display_json_results(results)
                
        except Exception as e:
            st.error(f"❌ Error analyzing claims: {str(e)}")

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

def display_json_results(results):
    """Display results in JSON format"""
    st.markdown("---")
    st.header("📋 Claims Analysis Results (JSON Format)")
    
    # Prepare JSON output
    json_results = []
    for i, result in enumerate(results, 1):
        try:
            # Try to parse the AI response as JSON
            analysis_text = result.get("analysis", "")
            if isinstance(analysis_text, str):
                json_start = analysis_text.find('{')
                json_end = analysis_text.rfind('}') + 1
                if json_start != -1 and json_end != 0:
                    analysis_json = json.loads(analysis_text[json_start:json_end])
                else:
                    analysis_json = {"raw_response": analysis_text}
            else:
                analysis_json = analysis_text
            
            claim_result = {
                "claim_id": i,
                "query": result["query"],
                "decision": analysis_json.get("decision", "Unknown"),
                "answers": analysis_json.get("answers", []),
                "relevant_clauses": [
                    {
                        "title": clause["title"],
                        "page_number": clause["page_number"],
                        "text": clause["text"][:200] + "..." if len(clause["text"]) > 200 else clause["text"]
                    }
                    for clause in result["relevant_clauses"]
                ]
            }
            json_results.append(claim_result)
            
        except json.JSONDecodeError:
            # Fallback for non-JSON responses
            claim_result = {
                "claim_id": i,
                "query": result["query"],
                "decision": "Unknown",
                "answers": [result.get("analysis", "")],
                "relevant_clauses": [
                    {
                        "title": clause["title"],
                        "page_number": clause["page_number"],
                        "text": clause["text"][:200] + "..." if len(clause["text"]) > 200 else clause["text"]
                    }
                    for clause in result["relevant_clauses"]
                ]
            }
            json_results.append(claim_result)
    
    # Display JSON
    st.json(json_results)
    
    # Download button
    json_str = json.dumps(json_results, indent=2)
    st.download_button(
        label="📥 Download Results as JSON",
        data=json_str,
        file_name=f"insurance_claims_analysis_{len(results)}_claims.json",
        mime="application/json"
    )
    
    # Reset button
    if st.button("🔄 New Analysis", key="new_json_analysis"):
        st.rerun()

def load_document_from_db(document_id):
    """Load a document from the database"""
    try:
        db_manager = st.session_state.db_manager
        
        # Load document info and clauses
        document_info = db_manager.get_document_by_id(document_id)
        structured_clauses = db_manager.get_clauses_by_document_id(document_id)
        
        if document_info and structured_clauses:
            # Update session state
            st.session_state.processed_document = document_info['filename']
            st.session_state.document_id = document_id
            st.session_state.structured_clauses = structured_clauses
            st.session_state.vector_index = {'type': 'chromadb', 'document_id': document_id}
            st.session_state.model = None
            
            st.success(f"✅ Loaded document '{document_info['filename']}' with {len(structured_clauses)} clauses")
            st.rerun()
        else:
            st.error("❌ Failed to load document from database")
    except Exception as e:
        st.error(f"❌ Error loading document: {str(e)}")

def load_document_from_db_silent(document_id):
    """Load a document from the database silently (for auto-restore)"""
    try:
        db_manager = st.session_state.db_manager
        
        # Load document info and clauses
        document_info = db_manager.get_document_by_id(document_id)
        structured_clauses = db_manager.get_clauses_by_document_id(document_id)
        
        if document_info and structured_clauses:
            # Update session state silently
            st.session_state.processed_document = document_info['filename']
            st.session_state.document_id = document_id
            st.session_state.structured_clauses = structured_clauses
            st.session_state.vector_index = {'type': 'chromadb', 'document_id': document_id}
            st.session_state.model = None
            return True
    except Exception:
        pass  # Silent fail
    return False

def display_single_result(result, claim_number):
    """Display a single claim result"""
    query = result["query"]
    relevant_clauses = result["relevant_clauses"]
    analysis_result = result["analysis"]
    
    # Query recap
    st.markdown(f"**Query {claim_number}:**")
    st.info(query)
    
    # AI Analysis
    st.markdown("**AI Coverage Analysis:**")
    
    if analysis_result:
        try:
            # Try to parse JSON response
            if isinstance(analysis_result, str):
                json_start = analysis_result.find('{')
                json_end = analysis_result.rfind('}') + 1
                if json_start != -1 and json_end != 0:
                    json_str = analysis_result[json_start:json_end]
                    parsed_result = json.loads(json_str)
                else:
                    raise ValueError("No JSON found in response")
            else:
                parsed_result = analysis_result
            
            # Display decision
            decision = parsed_result.get('decision', 'Unknown')
            amount = parsed_result.get('amount', 'Not specified')
            justification = parsed_result.get('justification', 'No justification provided')
            
            # Decision display with colors
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
    
    # Relevant clauses (collapsed)
    with st.expander(f"📄 Relevant Policy Clauses ({len(relevant_clauses)} found)"):
        for j, clause in enumerate(relevant_clauses, 1):
            st.markdown(f"**Clause {j}: {clause['title']} (Page {clause['page_number']})**")
            st.write(clause['text'])
            if j < len(relevant_clauses):
                st.markdown("---")

if __name__ == "__main__":
    main()
