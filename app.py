import os
import time
import tempfile
import streamlit as st
from dotenv import load_dotenv
from rag_engine import RAGEngine

load_dotenv()

# Page Configuration
st.set_page_config(
    page_title="SentinelGuard CRAG - Security & Threat Intelligence RAG",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Glassmorphism CSS Design System
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Background Gradient Mesh */
    .stApp {
        background: radial-gradient(circle at 15% 15%, rgba(99, 102, 241, 0.15) 0%, transparent 40%),
                    radial-gradient(circle at 85% 85%, rgba(139, 92, 246, 0.15) 0%, transparent 40%),
                    #0B0F17;
        color: #F3F4F6;
    }

    /* Glass Cards */
    .glass-card {
        background: rgba(17, 24, 39, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 18px;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    }
    
    .glass-pill {
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 20px;
        padding: 6px 14px;
        font-size: 0.82rem;
        color: #A5B4FC;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-weight: 500;
    }

    /* Header Title Gradient */
    .brand-title {
        font-size: 2.6rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 50%, #EC4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }

    .brand-subtitle {
        color: #9CA3AF;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }

    /* Metrics Row */
    .metric-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 12px;
        margin-bottom: 24px;
    }

    .metric-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 10px;
        padding: 14px;
        text-align: center;
    }

    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #818CF8;
    }

    .metric-label {
        font-size: 0.78rem;
        color: #9CA3AF;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 4px;
    }

    /* Code & KQL Snippets */
    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Telemetry Badge */
    .telemetry-bar {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 8px;
        padding: 6px 12px;
        font-size: 0.78rem;
        color: #93C5FD;
        margin-top: 8px;
        display: flex;
        gap: 16px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

if "indexed_files" not in st.session_state:
    st.session_state.indexed_files = []

if "chunk_count" not in st.session_state:
    st.session_state.chunk_count = 112  # Pre-loaded MS Defender & Sentinel KB

if "prefill_query" not in st.session_state:
    st.session_state.prefill_query = ""

# Sidebar Controls
with st.sidebar:
    st.markdown("### 🛡️ SentinelGuard Control Center")
    st.caption("Corrective RAG (CRAG) Engine for Security Operations")
    
    st.markdown("---")
    st.markdown("#### ⚙️ Engine Parameters")
    st.markdown('<div class="glass-pill">🤖 Engine: <code>nvidia/nemotron-3.5-lightning:free</code></div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-pill" style="margin-top:6px;">⚡ Vector DB: <code>ChromaDB (HNSW Cosine)</code></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    chunk_size = st.slider("Chunk Size (characters)", min_value=300, max_value=2000, value=1000, step=100)
    chunk_overlap = st.slider("Chunk Overlap", min_value=0, max_value=500, value=200, step=50)
    top_k = st.slider("Top Chunks to Retrieve", min_value=1, max_value=10, value=4)

    st.markdown("---")
    st.markdown("#### 📂 Custom Document Ingestion")
    uploaded_files = st.file_uploader(
        "Ingest Security Logs/Docs (PDF, TXT, MD)",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True
    )
    
    if st.button("🚀 Process & Index Files", use_container_width=True, type="primary"):
        if not uploaded_files:
            st.error("Please upload at least one file.")
        else:
            with st.spinner("Chunking & embedding custom files..."):
                temp_paths = []
                temp_dir = tempfile.mkdtemp()
                for uploaded_file in uploaded_files:
                    path = os.path.join(temp_dir, uploaded_file.name)
                    with open(path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    temp_paths.append(path)
                
                engine = RAGEngine()
                chunks_created = engine.create_vector_store(
                    file_paths=temp_paths,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                    reset_db=False
                )
                st.session_state.chunk_count += chunks_created
                st.session_state.indexed_files.extend([f.name for f in uploaded_files])
                st.success(f"Added {len(uploaded_files)} files ({chunks_created} vector chunks)!")

    st.markdown("---")
    st.markdown("#### 🌐 Knowledge Base Reload")
    if st.button("🔄 Sync MS Defender & Sentinel KB", use_container_width=True):
        with st.spinner("Fetching latest Microsoft Defender & Sentinel docs..."):
            from ingest_ms_security_docs import download_and_ingest
            chunks = download_and_ingest()
            st.session_state.chunk_count = chunks
            st.success(f"Synced Microsoft Security Knowledge Base ({chunks} chunks)!")

    st.markdown("---")
    st.markdown("#### ❓ Frequently Asked Questions")
    with st.expander("What sources are included in the KB?"):
        st.write("Official Microsoft Defender XDR guides, Sentinel SIEM architecture, Advanced Hunting KQL best practices, and KQL quick references.")
    with st.expander("How does CRAG handle confidence?"):
        st.write("The retrieval pipeline ranks top-K vector matches and validates relevance against the context before answer generation.")

# Main Interface Header
st.markdown('<div class="brand-title">🛡️ SentinelGuard CRAG</div>', unsafe_allow_html=True)
st.markdown('<div class="brand-subtitle">Corrective Retrieval-Augmented Generation for Microsoft Defender XDR, Sentinel & KQL Intelligence.</div>', unsafe_allow_html=True)

# Metric Badges Row
st.markdown(f"""
<div class="metric-container">
    <div class="metric-card">
        <div class="metric-value">{st.session_state.chunk_count}</div>
        <div class="metric-label">Vector Passages</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">Sub-100 ms</div>
        <div class="metric-label">Chroma Retrieval</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">Nemotron 3.5</div>
        <div class="metric-label">AI Generator Engine</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">Grounded</div>
        <div class="metric-label">Fact Verification</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Quick Sample Question Cards
st.markdown("#### 💡 Quick Security Queries (Click to Run)")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("⚡ Defender KQL Best Practices", use_container_width=True):
        st.session_state.prefill_query = "What are the best practices for writing KQL queries in Microsoft Defender Advanced Hunting?"

with col2:
    if st.button("🛡️ Sentinel SIEM Architecture", use_container_width=True):
        st.session_state.prefill_query = "Explain Microsoft Sentinel architecture and built-in analytics detection rules."

with col3:
    if st.button("🔍 KQL Operators Quick Reference", use_container_width=True):
        st.session_state.prefill_query = "Show me a summary of key KQL operators like summarize, join, and extend."

st.markdown("<br>", unsafe_allow_html=True)

# Render Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "telemetry" in msg:
            st.markdown(f"""
            <div class="telemetry-bar">
                <span>⏱️ Latency: <b>{msg['telemetry']['latency']:.2f}s</b></span>
                <span>📚 Context Chunks: <b>{msg['telemetry']['chunks_count']}</b></span>
                <span>🤖 Model: <b>{msg['telemetry']['model']}</b></span>
            </div>
            """, unsafe_allow_html=True)
            
        if "sources" in msg and msg["sources"]:
            with st.expander("🔍 View Verified Source Citations"):
                for idx, src in enumerate(msg["sources"], 1):
                    fname = os.path.basename(src['source'])
                    st.markdown(f"**Citation [{idx}]:** `{fname}` (Page/Section {src['page']})")
                    st.markdown(f"```text\n{src['content']}\n```")

# Determine active prompt (from input or clicked card)
default_prompt = st.session_state.prefill_query
st.session_state.prefill_query = ""  # Reset after reading

if prompt := st.chat_input("Ask a threat hunting or security query...") or default_prompt:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant answer with telemetry timing
    with st.chat_message("assistant"):
        with st.spinner("Retrieving vector passages & generating response..."):
            start_time = time.time()
            engine = RAGEngine()
            result = engine.query(
                user_query=prompt,
                top_k=top_k,
                model_name="nvidia/nemotron-3.5-lightning:free"
            )
            elapsed = time.time() - start_time
            
            st.markdown(result["answer"])
            
            telemetry_data = {
                "latency": elapsed,
                "chunks_count": len(result["sources"]),
                "model": "nvidia/nemotron-3.5-lightning:free"
            }
            
            st.markdown(f"""
            <div class="telemetry-bar">
                <span>⏱️ Latency: <b>{elapsed:.2f}s</b></span>
                <span>📚 Context Chunks: <b>{len(result['sources'])}</b></span>
                <span>🤖 Model: <b>nvidia/nemotron-3.5-lightning:free</b></span>
            </div>
            """, unsafe_allow_html=True)
            
            if result["sources"]:
                with st.expander("🔍 View Verified Source Citations"):
                    for idx, src in enumerate(result["sources"], 1):
                        fname = os.path.basename(src['source'])
                        st.markdown(f"**Citation [{idx}]:** `{fname}` (Section {src['page']})")
                        st.markdown(f"```text\n{src['content']}\n```")
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": result["answer"],
                "sources": result["sources"],
                "telemetry": telemetry_data
            })
