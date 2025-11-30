"""Streamlit UI for the QA Agent application."""
import streamlit as st
import requests
import json
from typing import List, Dict, Any
import os

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(
    page_title="QA Agent - Test Case Generator",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; font-weight: bold; color: #1f77b4; margin-bottom: 0.5rem; }
    .sub-header { font-size: 1.2rem; color: #666; margin-bottom: 2rem; }
    .success-box { padding: 1rem; background-color: #d4edda; border-radius: 0.5rem; border-left: 4px solid #28a745; }
    .error-box { padding: 1rem; background-color: #f8d7da; border-radius: 0.5rem; border-left: 4px solid #dc3545; }
    .info-box { padding: 1rem; background-color: #d1ecf1; border-radius: 0.5rem; border-left: 4px solid #17a2b8; }
    .test-case-card { padding: 1rem; background-color: #f8f9fa; border-radius: 0.5rem; margin-bottom: 1rem; border: 1px solid #dee2e6; }
    .stButton>button { width: 100%; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "test_cases" not in st.session_state:
    st.session_state.test_cases = []
if "knowledge_base_built" not in st.session_state:
    st.session_state.knowledge_base_built = False
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []
if "html_uploaded" not in st.session_state:
    st.session_state.html_uploaded = False
if "generated_scripts" not in st.session_state:
    st.session_state.generated_scripts = {}


def check_api_health() -> bool:
    """Check if the API is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False


def upload_documents(files) -> List[Dict]:
    """Upload documents to the API."""
    results = []
    files_data = [("files", (f.name, f.getvalue(), "application/octet-stream")) for f in files]
    try:
        response = requests.post(f"{API_BASE_URL}/api/upload/documents", files=files_data)
        if response.status_code == 200:
            return response.json().get("results", [])
    except Exception as e:
        st.error(f"Upload error: {str(e)}")
    return results


def upload_html(file) -> Dict:
    """Upload HTML file to the API."""
    try:
        files = {"file": (file.name, file.getvalue(), "text/html")}
        response = requests.post(f"{API_BASE_URL}/api/upload/html", files=files)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"HTML upload error: {str(e)}")
    return {}


def get_stats() -> Dict:
    """Get knowledge base statistics."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/stats")
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return {}


def generate_test_cases(query: str, n_context: int = 10) -> Dict:
    """Generate test cases via API."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/generate/test-cases",
            json={"query": query, "n_context": n_context},
            timeout=120
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Generation error: {str(e)}")
    return {}


def generate_selenium_script(test_case: Dict, html_filename: str) -> Dict:
    """Generate Selenium script via API."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/generate/selenium-script",
            json={"test_case": test_case, "html_filename": html_filename},
            timeout=120
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Script generation error: {str(e)}")
    return {}


def clear_knowledge_base():
    """Clear all data."""
    try:
        response = requests.delete(f"{API_BASE_URL}/api/clear")
        return response.status_code == 200
    except:
        return False


# Main UI
st.markdown('<p class="main-header">Autonomous QA Agent</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Generate test cases and Selenium scripts from your documentation</p>', unsafe_allow_html=True)

# Check API Status
api_healthy = check_api_health()
if not api_healthy:
    st.error("API server is not running. Please start the FastAPI server first: `python main.py`")
    st.stop()

# Sidebar - Status and Stats
with st.sidebar:
    st.header("System Status")
    
    stats = get_stats()
    kb_stats = stats.get("knowledge_base", {})
    
    st.metric("Total Chunks", kb_stats.get("total_chunks", 0))
    st.metric("Source Documents", kb_stats.get("unique_sources", 0))
    
    if kb_stats.get("sources"):
        st.subheader("Loaded Sources")
        for source in kb_stats.get("sources", []):
            st.text(f"• {source}")
    
    st.divider()
    
    if st.button("Clear Knowledge Base", type="secondary"):
        if clear_knowledge_base():
            st.session_state.test_cases = []
            st.session_state.knowledge_base_built = False
            st.session_state.uploaded_files = []
            st.session_state.html_uploaded = False
            st.session_state.generated_scripts = {}
            st.success("Knowledge base cleared!")
            st.rerun()

# Main Content - Tabs
tab1, tab2, tab3 = st.tabs(["Upload & Build", "Generate Test Cases", "Generate Scripts"])

# Tab 1: Upload and Build Knowledge Base
with tab1:
    st.header("Phase 1: Knowledge Base Ingestion")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Support Documents")
        st.caption("Upload MD, TXT, JSON, PDF files containing product specs, UI guides, etc.")
        
        doc_files = st.file_uploader(
            "Choose support documents",
            type=["md", "txt", "json", "pdf", "docx"],
            accept_multiple_files=True,
            key="doc_uploader"
        )
        
        if doc_files:
            if st.button("Upload Documents", key="upload_docs"):
                with st.spinner("Processing documents..."):
                    results = upload_documents(doc_files)
                    for result in results:
                        if result.get("status") == "success":
                            st.success(f"{result['filename']} - {result['chunks_created']} chunks")
                            st.session_state.uploaded_files.append(result['filename'])
                        else:
                            st.error(f"{result['filename']} - {result.get('message', 'Error')}")
    
    with col2:
        st.subheader("Target HTML File")
        st.caption("Upload the checkout.html file to test")
        
        html_file = st.file_uploader(
            "Choose HTML file",
            type=["html"],
            key="html_uploader"
        )
        
        if html_file:
            if st.button("Upload HTML", key="upload_html"):
                with st.spinner("Processing HTML..."):
                    result = upload_html(html_file)
                    if result.get("status") == "success":
                        st.success(f"{result['filename']} uploaded - {result['chunks_created']} chunks")
                        st.session_state.html_uploaded = True
                        st.session_state.html_filename = html_file.name
                    else:
                        st.error("Failed to upload HTML file")
    
    st.divider()
    
    # Build Knowledge Base Button
    if st.session_state.uploaded_files or st.session_state.html_uploaded:
        if st.button("Build Knowledge Base", type="primary", use_container_width=True):
            with st.spinner("Building knowledge base..."):
                response = requests.post(f"{API_BASE_URL}/api/build-knowledge-base")
                if response.status_code == 200:
                    st.session_state.knowledge_base_built = True
                    st.markdown('<div class="success-box"><strong>Knowledge Base Built Successfully!</strong></div>', unsafe_allow_html=True)
                    st.balloons()

# Tab 2: Generate Test Cases
with tab2:
    st.header("Phase 2: Test Case Generation")
    
    if not st.session_state.knowledge_base_built:
        st.warning("Please build the knowledge base first (Tab 1)")
    else:
        st.subheader("Ask the Agent")
        
        # Preset queries
        preset_queries = [
            "Generate all positive and negative test cases for the discount code feature",
            "Generate test cases for form validation",
            "Generate test cases for the shopping cart functionality",
            "Generate test cases for shipping method selection",
            "Generate test cases for the complete checkout flow",
            "Generate test cases for payment processing"
        ]
        
        selected_preset = st.selectbox("Or select a preset query:", ["Custom query..."] + preset_queries)
        
        if selected_preset == "Custom query...":
            query = st.text_area("Enter your test case generation request:", height=100, 
                                placeholder="E.g., Generate all test cases for the discount code feature including edge cases")
        else:
            query = selected_preset
            st.info(f"Selected: {query}")
        
        n_context = st.slider("Number of context chunks to retrieve:", 5, 20, 10)
        
        if st.button("Generate Test Cases", type="primary", disabled=not query):
            with st.spinner("Generating test cases... This may take a moment."):
                result = generate_test_cases(query, n_context)
                
                if result:
                    st.session_state.test_cases = result.get("test_cases", [])
                    
                    st.success(f"Generated {len(st.session_state.test_cases)} test cases!")
                    
                    # Show sources used
                    sources = result.get("sources_used", [])
                    if sources:
                        st.info(f"Sources referenced: {', '.join(sources)}")
        
        # Display Test Cases
        if st.session_state.test_cases:
            st.divider()
            st.subheader(f"Generated Test Cases ({len(st.session_state.test_cases)})")
            
            for i, tc in enumerate(st.session_state.test_cases):
                if tc.get("parse_error"):
                    st.warning("Could not parse test cases into structured format. Raw response:")
                    st.code(tc.get("raw_response", "No response"))
                    continue
                
                with st.expander(f"**{tc.get('test_id', f'TC-{i+1}')}**: {tc.get('feature', 'Unknown')} - {tc.get('test_scenario', '')[:50]}...", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**Feature:** {tc.get('feature', 'N/A')}")
                        st.markdown(f"**Scenario:** {tc.get('test_scenario', 'N/A')}")
                        st.markdown(f"**Type:** {tc.get('test_type', 'N/A')} | **Priority:** {tc.get('priority', 'N/A')}")
                        st.markdown(f"**Grounded In:** `{tc.get('grounded_in', 'N/A')}`")
                        
                        if tc.get("preconditions"):
                            st.markdown("**Preconditions:**")
                            for pre in tc.get("preconditions", []):
                                st.markdown(f"  - {pre}")
                        
                        if tc.get("test_steps"):
                            st.markdown("**Test Steps:**")
                            for j, step in enumerate(tc.get("test_steps", []), 1):
                                st.markdown(f"  {j}. {step}")
                        
                        if tc.get("test_data"):
                            st.markdown("**Test Data:**")
                            st.json(tc.get("test_data", {}))
                        
                        st.markdown(f"**Expected Result:** {tc.get('expected_result', 'N/A')}")
                    
                    with col2:
                        if st.button("Generate Script", key=f"gen_script_{i}"):
                            st.session_state.selected_test_case = tc
                            st.session_state.selected_test_index = i
                            st.info("Switch to 'Generate Scripts' tab to see the script")

# Tab 3: Generate Selenium Scripts
with tab3:
    st.header("Phase 3: Selenium Script Generation")
    
    if not st.session_state.test_cases:
        st.warning("Please generate test cases first (Tab 2)")
    else:
        st.subheader("Select a Test Case")
        
        # Create options for selectbox
        tc_options = []
        for i, tc in enumerate(st.session_state.test_cases):
            if not tc.get("parse_error"):
                tc_id = tc.get("test_id", f"TC-{i+1}")
                feature = tc.get("feature", "Unknown")
                scenario = tc.get("test_scenario", "")[:40]
                tc_options.append(f"{tc_id}: {feature} - {scenario}...")
        
        if tc_options:
            selected_idx = st.selectbox("Choose test case:", range(len(tc_options)), format_func=lambda x: tc_options[x])
            
            selected_tc = st.session_state.test_cases[selected_idx]
            
            # Show selected test case details
            with st.expander("Selected Test Case Details", expanded=True):
                st.json(selected_tc)
            
            # HTML filename
            html_filename = st.text_input("HTML Filename:", value=st.session_state.get("html_filename", "checkout.html"))
            
            if st.button("Generate Selenium Script", type="primary", use_container_width=True):
                with st.spinner("Generating Selenium script... This may take a moment."):
                    result = generate_selenium_script(selected_tc, html_filename)
                    
                    if result and result.get("status") == "success":
                        script = result.get("script", "")
                        st.session_state.generated_scripts[selected_tc.get("test_id", "unknown")] = script
                        
                        st.success("Script generated successfully!")
                        
                        st.subheader("Generated Selenium Script")
                        st.code(script, language="python")
                        
                        # Download button
                        test_id = selected_tc.get("test_id", "test").replace("-", "_").lower()
                        st.download_button(
                            label="Download Script",
                            data=script,
                            file_name=f"test_{test_id}.py",
                            mime="text/x-python"
                        )
        else:
            st.warning("No valid test cases available for script generation")

# Footer
st.divider()
st.caption("Autonomous QA Agent | Built with FastAPI + Streamlit + ChromaDB")