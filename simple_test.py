import streamlit as st
import sys
import os

st.title("🎉 Deployment Test")
st.write("If you can see this, the deployment is working!")

# Test basic functionality
st.success("✅ Streamlit is running successfully!")
st.write(f"Python version: {sys.version}")

# Test secrets
st.write("### Testing API Key Configuration")
try:
    api_key = st.secrets.get("PERPLEXITY_API_KEY", "Not found")
    if api_key != "Not found":
        st.success("✅ API Key found in Streamlit secrets!")
        st.write(f"API Key starts with: {api_key[:10]}...")
    else:
        # Try environment variable
        env_key = os.getenv("PERPLEXITY_API_KEY")
        if env_key:
            st.success("✅ API Key found in environment!")
            st.write(f"API Key starts with: {env_key[:10]}...")
        else:
            st.warning("⚠️ No API key found in secrets or environment")
except Exception as e:
    st.error(f"❌ Secrets error: {e}")

# Test core dependencies
st.write("### Testing Core Dependencies")

dependencies = [
    ('numpy', 'NumPy'),
    ('sklearn', 'Scikit-learn'), 
    ('fitz', 'PyMuPDF'),
    ('requests', 'Requests')
]

for module_name, display_name in dependencies:
    try:
        __import__(module_name)
        st.success(f"✅ {display_name} imported successfully")
    except ImportError as e:
        st.error(f"❌ {display_name} import failed: {e}")

st.balloons()
