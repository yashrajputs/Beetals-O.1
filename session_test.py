import streamlit as st
import time
from datetime import datetime

# Test session state persistence behavior
st.title("🔍 Session State Persistence Test")

# Initialize session state values
if 'counter' not in st.session_state:
    st.session_state.counter = 0
if 'timestamp' not in st.session_state:
    st.session_state.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
if 'test_data' not in st.session_state:
    st.session_state.test_data = {
        'processed_document': None,
        'vector_index': None,
        'structured_clauses': None
    }

# Display current state
st.header("Current Session State")
col1, col2 = st.columns(2)

with col1:
    st.metric("Counter", st.session_state.counter)
    st.text(f"Session started: {st.session_state.timestamp}")

with col2:
    st.json(st.session_state.test_data)

# Test buttons
st.header("Session State Tests")

if st.button("Increment Counter"):
    st.session_state.counter += 1
    st.success(f"Counter increased to {st.session_state.counter}")
    st.rerun()

if st.button("Add Test Data"):
    st.session_state.test_data['processed_document'] = f"test_doc_{st.session_state.counter}"
    st.session_state.test_data['vector_index'] = {'type': 'test', 'id': st.session_state.counter}
    st.session_state.test_data['structured_clauses'] = [
        {'title': f'Test Clause {st.session_state.counter}', 'text': 'Test content'}
    ]
    st.success("Test data added to session state")
    st.rerun()

if st.button("Clear Session State"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.success("Session state cleared")
    st.rerun()

# Information about session state behavior
st.header("📋 Session State Behavior Analysis")

st.markdown("""
### Why `st.session_state` is Lost:

**✅ Normal Behavior (Data Persists):**
- Clicking buttons within the same session
- Widget interactions (sliders, text input, etc.)
- Re-running the script with `st.rerun()`
- Navigation between pages in multi-page apps

**❌ Data Loss Scenarios:**
1. **Browser refresh (F5)** - Streamlit restarts the script from scratch
2. **Browser tab closure and reopening**
3. **Server restart** (local development or cloud deployment)
4. **Session timeout** (especially on Streamlit Cloud)
5. **Memory cleanup** when server is idle

### Current Test Results:
- **Counter**: Shows if session persists during interactions
- **Timestamp**: Shows when this session started
- **Test Data**: Simulates your app's document data

### Solutions for Persistence:
1. **Database Storage** (Your current approach ✅)
2. **File-based storage** (JSON, pickle files)
3. **Cloud storage** (S3, Google Drive)
4. **URL parameters** for critical state
5. **Cookies** for user preferences
""")

# Real-time session info
st.header("🔄 Real-time Session Info")
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
session_duration = (datetime.now() - datetime.strptime(st.session_state.timestamp, "%Y-%m-%d %H:%M:%S")).seconds

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Current Time", current_time)
with col2:
    st.metric("Session Duration", f"{session_duration}s")
with col3:
    st.metric("Total Keys in Session", len(st.session_state.keys()))

# Auto-refresh option
if st.checkbox("Auto-refresh every 5 seconds"):
    time.sleep(5)
    st.rerun()
