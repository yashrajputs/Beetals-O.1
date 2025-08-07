import streamlit as st
import os

# Streamlit page configuration
try:
    st.set_page_config(
        page_title="Insurance Claims Analysis Demo",
        page_icon="🏥",
        layout="wide"
    )
except Exception:
    pass

st.title("🏥 Insurance Claims Analysis System")
st.markdown("### Demo Version - Working with Mock Data")

# API Key check
api_key = os.getenv("PERPLEXITY_API_KEY")
if not api_key:
    try:
        api_key = st.secrets["PERPLEXITY_API_KEY"]
    except (KeyError, FileNotFoundError):
        st.warning("⚠️ API key not configured. Demo will use mock responses.")
        api_key = None

if api_key:
    st.success("✅ API Key configured successfully!")

# Demo functionality
st.markdown("---")
st.header("🔍 Demo Claims Analysis")

st.info("""
**Demo Mode**: This version uses sample insurance policy data to demonstrate the functionality.
The full version with PDF upload will be available once all dependencies are installed.
""")

# Sample queries
st.subheader("Try Sample Insurance Queries")

sample_queries = [
    "50M, used air ambulance, distance traveled 300 km, seeking 100% reimbursement",
    "35F, pre-existing diabetes, hospitalization for 5 days",
    "28M, outpatient surgery, day care procedure claim",
    "45F, maternity expenses, normal delivery claim"
]

selected_query = st.selectbox("Select a sample query:", ["Choose a query..."] + sample_queries)

if selected_query != "Choose a query...":
    if st.button("🔍 Analyze Claim", type="primary"):
        with st.spinner("Analyzing claim..."):
            # Simulate analysis
            import time
            time.sleep(2)
            
            st.markdown("---")
            st.header("📋 Analysis Results")
            
            # Mock analysis results based on query
            if "air ambulance" in selected_query.lower():
                decision = "Partially Covered"
                st.warning(f"⚠️ **Coverage Decision:** {decision}")
                st.markdown("""
                **📝 Analysis:**
                - Air ambulance services are covered up to Rs. 2,000 per incident
                - Distance-based charges may apply for distances over 100 km
                - 300 km distance exceeds standard coverage limits
                - Additional charges may be out-of-pocket
                """)
            elif "pre-existing" in selected_query.lower():
                decision = "No"
                st.error(f"❌ **Coverage Decision:** {decision}")
                st.markdown("""
                **📝 Analysis:**
                - Pre-existing diabetes has a waiting period of 2-4 years
                - Hospitalization related to pre-existing conditions not covered during waiting period
                - Coverage available after waiting period completion
                - Emergency treatment may be covered subject to conditions
                """)
            elif "outpatient surgery" in selected_query.lower():
                decision = "Yes"
                st.success(f"✅ **Coverage Decision:** {decision}")
                st.markdown("""
                **📝 Analysis:**
                - Day care procedures are covered under the policy
                - Outpatient surgery is included in coverage
                - Pre-authorization may be required
                - Coverage up to policy limits applies
                """)
            else:
                decision = "Yes"
                st.success(f"✅ **Coverage Decision:** {decision}")
                st.markdown("""
                **📝 Analysis:**
                - Claim appears to be covered under standard policy terms
                - Subject to policy limits and conditions
                - Documentation required for processing
                - Contact customer service for claim submission
                """)
            
            # Show relevant policy sections
            st.subheader("📄 Relevant Policy Clauses")
            with st.expander("Coverage Details (Page 1)"):
                st.write("This policy provides comprehensive health insurance coverage for the insured person including hospitalization expenses, day care procedures, and emergency services.")
            
            with st.expander("Benefits (Page 2)"):
                st.write("Benefits include hospitalization expenses up to policy limit, pre and post hospitalization expenses, day care procedures, and emergency ambulance services.")
            
            with st.expander("Emergency Services (Page 5)"):
                st.write("Emergency ambulance services are covered up to Rs. 2,000 per incident. Air ambulance services may be covered subject to policy terms.")

# Footer
st.markdown("---")
st.markdown("""
**🚧 Demo Version Notes:**
- This demo uses sample data and mock AI responses
- Full PDF processing will be available once dependencies are resolved
- Real-time AI analysis requires proper API configuration
""")

st.success("✅ Demo is working! Ready to upgrade to full version with PDF support.")
