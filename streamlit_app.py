import streamlit as st
import requests
import os

# Configure the page
st.set_page_config(
    page_title="Multimodal RAG Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE = os.getenv("API_BASE", "http://localhost:8002")  # Your deployed backend
ADMIN_PASSWORD = "admin123"  # Change this to your desired password

# Clean and elegant styling
st.markdown("""
<style>
    /* Reset and clean layout - compact */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 1200px;
    }
    
    /* Header - more compact */
    .main-header {
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 1.5rem;
        border-bottom: 1px solid #e9ecef;
    }
    
    /* Admin section */
    .admin-success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Upload section - clean and compact */
    .upload-section {
        padding: 1rem 0;
        margin: 1rem 0;
    }
    
    /* Make upload section text much bigger */
    .upload-section .stTextInput > label > div {
        font-size: 1.4rem !important;
        font-weight: 700 !important;
        color: #333 !important;
    }
    
    .upload-section .stTextInput input {
        font-size: 1.2rem !important;
        padding: 1rem !important;
        height: 3rem !important;
    }
    
    .upload-section .stFileUploader > label > div {
        font-size: 1.4rem !important;
        font-weight: 700 !important;
        color: #333 !important;
    }
    
    .upload-section .stFileUploader section {
        font-size: 1.2rem !important;
    }
    
    .upload-section .stFileUploader section button {
        font-size: 1.1rem !important;
        padding: 0.8rem 1.2rem !important;
    }
    
    .upload-section .stButton > button {
        font-size: 1.2rem !important;
        padding: 1rem 1.5rem !important;
        height: 3rem !important;
        font-weight: 700 !important;
    }
    
    /* Make text bigger throughout the app */
    .stTextInput > label {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.5rem !important;
    }
    
    .stTextInput > div > div > input {
        font-size: 1rem !important;
        padding: 0.75rem !important;
        height: auto !important;
        min-height: 2.5rem !important;
    }
    
    .stFileUploader > label {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }
    
    .stFileUploader section {
        font-size: 1rem !important;
    }
    
    .stSelectbox > label {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }
    
    .stSelectbox > div > div {
        font-size: 1rem !important;
    }
    
    /* Sidebar text bigger */
    .sidebar .stMarkdown {
        font-size: 1rem !important;
    }
    
    .sidebar h3 {
        font-size: 1.3rem !important;
    }
    
    .sidebar .stTextInput > label {
        font-size: 1rem !important;
    }
    
    .sidebar .stButton > button {
        font-size: 1rem !important;
        padding: 0.6rem 1rem !important;
        height: auto !important;
        min-height: 2.2rem !important;
    }
    
    /* Main buttons bigger */
    .stButton > button {
        font-size: 1.1rem !important;
        padding: 0.75rem 1.5rem !important;
        height: auto !important;
        min-height: 2.5rem !important;
        font-weight: 600 !important;
    }
    
    /* Main content text bigger */
    .stMarkdown h2 {
        font-size: 1.8rem !important;
    }
    
    .stMarkdown h3 {
        font-size: 1.5rem !important;
    }
    
    .stMarkdown p {
        font-size: 1.1rem !important;
    }
    
    /* Force full width for question container */
    .question-container {
        width: 100% !important;
        max-width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Stronger CSS overrides for the main input */
    .question-container .stTextInput,
    .question-container .stTextInput > div,
    .question-container .stTextInput > div > div {
        width: 100% !important;
        max-width: 100% !important;
        margin: 0 !important;
    }
    
    .question-container .stTextInput > div > div > input {
        font-size: 1.2rem !important;
        padding: 1rem 1.2rem !important;
        height: 3.5rem !important;
        width: 100% !important;
        max-width: 100% !important;
        border: 2px solid #e3f2fd !important;
        border-radius: 10px !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1) !important;
        background: #fafafa !important;
        box-sizing: border-box !important;
        margin: 0 !important;
        flex-grow: 1 !important;
    }
    
    .question-container .stTextInput > div > div > input:focus {
        border-color: #1976d2 !important;
        box-shadow: 0 0 0 0.2rem rgba(25, 118, 210, 0.15) !important;
        background: white !important;
        outline: none !important;
    }
    
    /* Override any Streamlit container restrictions */
    .question-container .element-container {
        width: 100% !important;
        max-width: 100% !important;
    }
    
    /* Make the main button more attractive */
    .stButton > button[kind="primary"] {
        background: linear-gradient(45deg, #1976d2, #1565c0) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 1rem 2rem !important;
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        height: 3.5rem !important;
        box-shadow: 0 4px 12px rgba(25, 118, 210, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(25, 118, 210, 0.4) !important;
    }
    
    /* Message styling - simple and clean */
    .message-user {
        background: #e3f2fd;
        color: #1565c0;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin: 1rem 0 1rem 3rem;
        border-left: 4px solid #1976d2;
    }
    
    .message-assistant {
        background: #f5f5f5;
        color: #424242;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin: 1rem 3rem 1rem 0;
        border-left: 4px solid #757575;
    }
    
    .chat-history {
        background: #fafafa;
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 2rem;
        border: 1px solid #e9ecef;
        max-height: 400px;
        overflow-y: auto;
    }
    

    
    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 3rem;
        background: #f8f9fa;
        border-radius: 12px;
        border: 1px dashed #dee2e6;
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Main header - compact
st.markdown("""
<div class="main-header">
    <h1 style="font-size: 1.8rem; margin-bottom: 0.3rem;">📚 Multimodal RAG Assistant</h1>
    <p style="font-size: 1rem; color: #666; margin: 0;">
        Upload documents and ask intelligent questions using AI-powered search
    </p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'selected_product' not in st.session_state:
    st.session_state.selected_product = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'admin_authenticated' not in st.session_state:
    st.session_state.admin_authenticated = False

# Admin Authentication Section
with st.sidebar:
    st.markdown("### 🔐 Admin Access")
    
    if not st.session_state.admin_authenticated:
        # Login form
        with st.container():
            admin_password = st.text_input("Enter Admin Password", type="password", key="admin_pwd", placeholder="Enter password...")
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("🔑 Login", type="primary", key="login_btn"):
                    if admin_password == ADMIN_PASSWORD:
                        st.session_state.admin_authenticated = True
                        st.success("✅ Admin access granted!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid password!")
    else:
        # Admin is logged in
        st.markdown("""
        <div class="admin-success">
            <strong>🔓 Admin Mode Active</strong><br>
            <small>You can now upload documents</small>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚪 Logout", key="logout_btn"):
            st.session_state.admin_authenticated = False
            st.rerun()
    
    st.markdown("---")

# Admin Upload Section (only visible when authenticated)
if st.session_state.admin_authenticated:
    st.markdown("## 📤 Document Upload")
    
    with st.container():
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            upload_product = st.text_input(
                "📁 Product Name", 
                key="upload_product",
                placeholder="e.g., CV, Product Manual, etc.",
                help="Enter a unique name for your document category"
            )
        
        with col2:
            uploaded_file = st.file_uploader(
                "📄 Choose PDF File",
                type=['pdf'],
                help="Upload a PDF document for processing"
            )
        
        if uploaded_file is not None and upload_product.strip():
            st.markdown(f"**File:** {uploaded_file.name} ({uploaded_file.size:,} bytes)")
            
            col1, col2, col3 = st.columns([1, 1, 2])
            with col2:
                if st.button("🚀 Upload & Process", type="primary", key="upload_btn"):
                    with st.spinner("🔄 Uploading and processing document..."):
                        try:
                            # Read file into memory
                            file_bytes = uploaded_file.getvalue()
                            
                            # Upload to backend
                            files = {"file": (uploaded_file.name, file_bytes)}
                            headers = {"x-api-key": "admin123"}
                            
                            response = requests.post(
                                f"{API_BASE}/admin/upload",
                                files=files,
                                headers=headers,
                                params={"product": upload_product}
                            )
                            
                            if response.status_code == 200:
                                result = response.json()
                                st.success("✅ Document uploaded successfully!")
                                st.markdown(f"""
                                **Upload Details:**
                                - 📁 Product: `{result['product']}`
                                - 📄 File: `{result['filename']}`
                                - 🧩 Chunks processed: `{result['chunks_stored']}`
                                """)
                                st.rerun()
                            else:
                                st.error(f"❌ Upload failed: {response.text}")
                                
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
        
        elif uploaded_file is not None and not upload_product.strip():
            st.warning("⚠️ Please enter a product name before uploading.")
        
        st.markdown('</div>', unsafe_allow_html=True)

# Sidebar for product and document selection (for all users)
with st.sidebar:
    st.markdown("### 🗂️ Available Products")
    
    # Fetch available products and documents from backend
    try:
        resp = requests.get(f"{API_BASE}/products")
        if resp.status_code == 200:
            products_data = resp.json()
            products = list(products_data.keys())
        else:
            st.error("❌ Failed to fetch products")
            products = []
            products_data = {}
    except Exception as e:
        st.error(f"❌ Connection error: {str(e)}")
        products = []
        products_data = {}

    if products:
        # Enhanced product selection
        product = st.selectbox(
            "📋 Choose a product to query:",
            products,
            index=0 if st.session_state.selected_product is None else (
                products.index(st.session_state.selected_product) if st.session_state.selected_product in products else 0
            ),
            help="Select which document collection you want to ask questions about"
        )
        st.session_state.selected_product = product
        
        # Show documents for the selected product
        docs = products_data.get(product, [])
        if docs:
            st.markdown(f"**📄 Documents in {product}:**")
            for doc in docs:
                st.markdown(f"• {doc}")
        else:
            st.warning(f"⚠️ No documents found for {product}")
            
        # Quick stats
        total_docs = sum(len(docs) for docs in products_data.values())
        st.markdown(f"**📊 Total: {len(products)} products, {total_docs} documents**")
    else:
        st.warning("⚠️ No products available. Upload documents to get started!")

# Check if product is selected and has documents
if not st.session_state.selected_product or not products_data.get(st.session_state.selected_product):
    st.markdown("""
    <div class="empty-state">
        <h3>⚠️ No Product Selected</h3>
        <p>Please select a product with uploaded documents from the sidebar to start asking questions.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Compact spacing
st.markdown('<div style="margin: 1rem 0;"></div>', unsafe_allow_html=True)

# Simple and attractive chat section - more compact
st.markdown(f"""
<div style="text-align: center; margin-bottom: 1.5rem;">
    <h2 style="color: #1976d2; font-size: 1.8rem; margin-bottom: 0.3rem;">
        💬 Chat with {st.session_state.selected_product}
    </h2>
    <p style="color: #666; font-size: 1.1rem; margin: 0;">
        📁 {len(products_data.get(st.session_state.selected_product, []))} document{'s' if len(products_data.get(st.session_state.selected_product, [])) != 1 else ''} ready to answer your questions
    </p>
</div>
""", unsafe_allow_html=True)

# Question Input - more compact
st.markdown("""
<div style="background: white; padding: 1.5rem; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin: 1rem 0;">
    <h3 style="color: #333; margin-bottom: 0.8rem; text-align: center;">✨ What would you like to know?</h3>
</div>
""", unsafe_allow_html=True)

# Force full width container
st.markdown('<div class="question-container">', unsafe_allow_html=True)

question = st.text_input(
    "Type your question here...",
    placeholder="e.g., Tell me about work experience, skills, projects, education...",
    key="question_input",
    label_visibility="collapsed"
)

st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div style="margin: 1rem 0;"></div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    ask_clicked = st.button("🚀 Get Answer", type="primary", use_container_width=True)

# Process question
if ask_clicked and question.strip():
    with st.spinner("🤖 Getting answer..."):
        try:
            response = requests.post(
                f"{API_BASE}/rag/query",
                json={"question": question, "product": st.session_state.selected_product}
            )
            
            if response.status_code == 200:
                answer = response.json()["answer"]
                # Add to chat history
                st.session_state.chat_history.append({
                    "question": question,
                    "answer": answer,
                    "product": st.session_state.selected_product
                })
                st.rerun()
            else:
                st.error(f"❌ Server Error: {response.text}")
        except Exception as e:
            st.error(f"❌ Connection Error: {str(e)}")

elif ask_clicked and not question.strip():
    st.warning("⚠️ Please enter a question first!")

# Chat History Section
if st.session_state.chat_history:
    st.markdown('<div style="margin: 2rem 0;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="chat-history">', unsafe_allow_html=True)
    
    # Header
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 📝 Conversation History")
    with col3:
        if st.button("🗑️ Clear All", key="clear_all"):
            st.session_state.chat_history = []
            st.rerun()
    
    st.markdown("---")
    
    # Display conversations - clean and simple
    for i, chat in enumerate(reversed(st.session_state.chat_history)):
        # Question
        st.markdown(f"""
        <div class="message-user">
            <strong>❓ Your Question:</strong><br>
            {chat['question']}
        </div>
        """, unsafe_allow_html=True)
        
        # Answer
        st.markdown(f"""
        <div class="message-assistant">
            <strong>🤖 Answer:</strong><br>
            {chat['answer']}
        </div>
        """, unsafe_allow_html=True)
        
        # Delete option
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        with col4:
            if st.button("🗑️ Delete", key=f"delete_{i}"):
                st.session_state.chat_history.pop(-(i+1))
                st.rerun()
        
        # Separator
        if i < len(st.session_state.chat_history) - 1:
            st.markdown("---")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
else:
    # Empty state
    st.markdown("""
    <div class="empty-state">
        <div style="font-size: 2rem; margin-bottom: 1rem;">💭</div>
        <h3>No Conversations Yet</h3>
        <p>Ask a question above to start your conversation!</p>
    </div>
    """, unsafe_allow_html=True)

# Footer - compact
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #888; padding: 0.5rem;'>
        <p style='margin: 0; font-size: 0.8rem;'>
            🚀 Built with <strong>Streamlit</strong> • 
            ⚡ Powered by <strong>FastAPI</strong> • 
            🧠 Enhanced with <strong>OpenAI GPT-4</strong>
        </p>
    </div>
    """,
    unsafe_allow_html=True
) 