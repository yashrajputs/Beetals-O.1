import streamlit as st

st.title("🎉 Hello World!")
st.write("If you can see this, Streamlit deployment is working!")

st.success("✅ Success! The app is running on Streamlit Cloud.")

# Test secrets
try:
    secret = st.secrets["PERPLEXITY_API_KEY"]
    st.info(f"🔑 Secret found: {secret[:10]}...")
except:
    st.warning("⚠️ No secret found, but that's okay for testing!")

st.balloons()
