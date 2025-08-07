import streamlit as st
import os

st.set_page_config(
    page_title="Test App",
    page_icon="🧪",
)

st.title("🧪 Deployment Test")
st.write("This is a test to verify Streamlit Cloud deployment works.")

# Test API key access
api_key = os.getenv("PERPLEXITY_API_KEY")
if not api_key:
    try:
        api_key = st.secrets["PERPLEXITY_API_KEY"]
        st.success("✅ API Key found in Streamlit secrets!")
    except (KeyError, FileNotFoundError):
        st.error("❌ API Key not found")
        st.stop()
else:
    st.success("✅ API Key found in environment!")

st.write(f"API Key starts with: {api_key[:10]}...")

# Test imports
try:
    from utils.pdf_processor import extract_structured_sections, is_valid_pdf
    st.success("✅ PDF Processor imported successfully")
except Exception as e:
    st.error(f"❌ PDF Processor import failed: {e}")

try:
    from utils.vector_search import create_vector_index, get_top_similar_clauses
    st.success("✅ Vector Search imported successfully")
except Exception as e:
    st.error(f"❌ Vector Search import failed: {e}")

try:
    from utils.ai_analyzer import analyze_claim_with_ai
    st.success("✅ AI Analyzer imported successfully")
except Exception as e:
    st.error(f"❌ AI Analyzer import failed: {e}")

st.write("### Test Complete!")
st.write("If all items above show ✅, the main app should work.")
