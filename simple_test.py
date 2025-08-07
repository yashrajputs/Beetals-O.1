import streamlit as st

st.title("🎉 Deployment Test")
st.write("If you can see this, the deployment is working!")

# Test basic functionality
st.success("✅ Streamlit is running successfully!")

# Test environment
import sys
st.write(f"Python version: {sys.version}")

# Test secrets
import os
try:
    api_key = st.secrets.get("PERPLEXITY_API_KEY", "Not found")
    if api_key != "Not found":
        st.success("✅ Secrets are working!")
        st.write(f"API Key starts with: {api_key[:10]}...")
    else:
        st.warning("⚠️ No API key found in secrets")
except Exception as e:
    st.error(f"❌ Secrets error: {e}")

st.balloons()
