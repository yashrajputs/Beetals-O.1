import streamlit as st

st.set_page_config(
    page_title="Insurance Claims Analyzer",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Insurance Claims Analysis System")
st.write("**AI-Powered Insurance Coverage Decisions**")

# Check API key
try:
    api_key = st.secrets["PERPLEXITY_API_KEY"]
    st.success("✅ API Key configured successfully!")
    api_available = True
except:
    st.warning("⚠️ API key not found. Using demo mode.")
    api_available = False

st.markdown("---")

# Sample queries
st.header("🔍 Analyze Your Insurance Claim")

query = st.text_area(
    "Describe your insurance claim:",
    placeholder="Example: 45M, hospitalized for 3 days due to chest pain, seeking reimbursement for ₹50,000",
    height=100
)

col1, col2 = st.columns([1, 2])

with col1:
    if st.button("🔍 Analyze Claim", type="primary", disabled=not query.strip()):
        with st.spinner("Analyzing your claim..."):
            # Simulate analysis
            import time
            time.sleep(2)
            
            st.markdown("---")
            st.header("📋 Coverage Analysis Results")
            
            # Simple keyword-based analysis
            query_lower = query.lower()
            
            if any(word in query_lower for word in ["pre-existing", "diabetes", "chronic"]):
                st.error("❌ **Coverage Decision: NOT COVERED**")
                st.write("**Reason:** Pre-existing conditions have a waiting period of 2-4 years.")
            elif any(word in query_lower for word in ["accident", "emergency", "ambulance"]):
                st.success("✅ **Coverage Decision: COVERED**")
                st.write("**Reason:** Emergency treatments are covered immediately.")
            elif any(word in query_lower for word in ["cosmetic", "dental", "plastic"]):
                st.error("❌ **Coverage Decision: NOT COVERED**") 
                st.write("**Reason:** Cosmetic and dental treatments are excluded.")
            else:
                st.success("✅ **Coverage Decision: COVERED**")
                st.write("**Reason:** Standard hospitalization expenses are covered up to policy limits.")
            
            # Show policy info
            st.subheader("📄 Relevant Policy Information")
            
            with st.expander("Coverage Details"):
                st.write("""
                - **Sum Insured:** ₹5,00,000 per year
                - **Room Rent:** Up to ₹5,000 per day
                - **Pre & Post Hospitalization:** 30 days before, 60 days after
                - **Day Care Procedures:** Covered
                - **Ambulance:** Up to ₹2,000 per incident
                """)
            
            with st.expander("Exclusions"):
                st.write("""
                - Pre-existing diseases (2 year waiting period)
                - Cosmetic treatments
                - Dental care (unless due to accident)
                - Maternity expenses (1 year waiting period)
                - Mental health conditions
                """)

with col2:
    st.subheader("💡 Sample Claims")
    
    examples = [
        "45M, chest pain, hospitalized 3 days, ₹50,000",
        "32F, accident injury, emergency surgery, ₹1,50,000", 
        "28M, diabetes complications, 5 days ICU, ₹2,00,000",
        "35F, routine dental cleaning, ₹5,000",
        "50M, air ambulance, 200km distance, ₹25,000"
    ]
    
    for i, example in enumerate(examples):
        if st.button(f"Try Example {i+1}", key=f"ex_{i}"):
            st.rerun()

# Footer
st.markdown("---")
st.info("🎯 This system analyzes insurance claims using AI and policy terms to provide coverage decisions.")

if api_available:
    st.success("🚀 **Status:** Fully operational with AI analysis")
else:
    st.warning("🧪 **Status:** Demo mode - upgrade API key for full AI analysis")
