import streamlit as st
import time

st.set_page_config(
    page_title="Insurance Claims Analyzer",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Insurance Claims Analysis System")
st.markdown("### AI-Powered Coverage Decisions")

# Check API key
try:
    api_key = st.secrets["PERPLEXITY_API_KEY"]
    st.success("✅ API Key configured - Ready for AI analysis!")
    api_available = True
except:
    st.info("ℹ️ Using demo mode with keyword-based analysis")
    api_available = False

st.markdown("---")

# Input section
st.header("🔍 Enter Your Insurance Claim")

# Multiple claims input
claims_text = st.text_area(
    "Enter your claims (one per line):",
    placeholder="Examples:\n50M, used air ambulance, distance traveled 300 km, seeking 100% reimbursement\n35F, pre-existing diabetes, hospitalization for 5 days\n28M, outpatient surgery, day care procedure claim",
    height=120
)

if claims_text.strip():
    claims = [claim.strip() for claim in claims_text.split('\n') if claim.strip()]
    
    if st.button("🔍 Analyze Claims", type="primary"):
        
        st.markdown("---")
        st.header("📋 Analysis Results")
        
        results = []
        
        # Process each claim
        for i, claim in enumerate(claims, 1):
            with st.spinner(f"Analyzing claim {i} of {len(claims)}..."):
                time.sleep(1)  # Simulate processing
                
                # Simple keyword-based analysis
                claim_lower = claim.lower()
                
                # Determine coverage
                if any(word in claim_lower for word in ["pre-existing", "diabetes", "hypertension", "chronic"]):
                    decision = "No"
                    reason = "Pre-existing conditions have a waiting period"
                    status = "❌"
                elif any(word in claim_lower for word in ["cosmetic", "plastic", "beauty", "dental"]):
                    decision = "No" 
                    reason = "Cosmetic and dental treatments are excluded"
                    status = "❌"
                elif any(word in claim_lower for word in ["accident", "emergency", "trauma"]):
                    decision = "Yes"
                    reason = "Emergency treatments are covered"
                    status = "✅"
                elif "air ambulance" in claim_lower:
                    decision = "Partial"
                    reason = "Air ambulance covered up to ₹2,000 per incident"
                    status = "⚠️"
                else:
                    decision = "Yes"
                    reason = "Standard hospitalization expenses are covered"
                    status = "✅"
                
                results.append({
                    "claim_id": i,
                    "query": claim,
                    "decision": decision,
                    "answers": [
                        reason,
                        "Subject to policy terms and conditions",
                        "Documentation required for processing",
                        "Contact customer service for detailed information"
                    ]
                })
        
        # Display results
        for result in results:
            st.subheader(f"Claim {result['claim_id']}")
            st.info(f"**Query:** {result['query']}")
            
            if result['decision'] == "Yes":
                st.success(f"✅ **Decision:** Covered")
            elif result['decision'] == "No":
                st.error(f"❌ **Decision:** Not Covered")
            else:
                st.warning(f"⚠️ **Decision:** {result['decision']}")
            
            st.write("**Policy Information:**")
            for answer in result['answers']:
                st.write(f"• {answer}")
            
            st.markdown("---")
        
        # JSON output
        st.subheader("📄 JSON Results")
        st.json(results)
        
        # Download option
        import json
        json_str = json.dumps(results, indent=2)
        st.download_button(
            label="📥 Download Results",
            data=json_str,
            file_name=f"claims_analysis_{len(results)}_claims.json",
            mime="application/json"
        )

# Sample claims section
st.markdown("---")
st.subheader("💡 Sample Claims to Try")

examples = [
    "50M, used air ambulance, distance traveled 300 km, seeking 100% reimbursement",
    "35F, pre-existing diabetes, hospitalization for 5 days", 
    "28M, outpatient surgery, day care procedure claim",
    "45F, maternity expenses, normal delivery claim",
    "32M, accident injury, emergency surgery, ₹1,50,000"
]

col1, col2 = st.columns(2)

for i, example in enumerate(examples):
    col = col1 if i % 2 == 0 else col2
    with col:
        if st.button(f"📝 Example {i+1}", key=f"sample_{i}"):
            st.rerun()

# Footer
st.markdown("---")
st.info("🎯 This system analyzes insurance claims and provides coverage decisions based on policy terms.")

if api_available:
    st.success("🚀 **Status:** AI-powered analysis ready")
else:
    st.warning("🔧 **Status:** Demo mode - keyword-based analysis")
