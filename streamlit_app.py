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

API_BASE = os.getenv("API_BASE", "http://localhost:8002")  # Update if backend runs elsewhere
ADMIN_PASSWORD = "admin123"  # Change this to your desired password

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 2rem;
    }
    .admin-success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 0.75rem;
        margin: 0.5rem 0;
    }
    .upload-section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .chat-container {
        background-color: #ffffff;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stButton > button {
        width: 100%;
        border-radius: 0.5rem;
        height: 2.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1>📚 Multimodal RAG Assistant</h1>
    <p style="font-size: 1.1rem; color: #666; margin-top: 0.5rem;">
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

# Main chat interface
st.markdown("## 💬 Ask Questions")

# Check if product is selected and has documents
if not st.session_state.selected_product or not products_data.get(st.session_state.selected_product):
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background-color: #fff3cd; border-radius: 0.5rem; margin: 1rem 0;">
        <h3>⚠️ No Product Selected</h3>
        <p>Please select a product with uploaded documents from the sidebar to start asking questions.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Question input section
with st.container():
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        question = st.text_input(
            f"💭 Ask about **{st.session_state.selected_product}**:",
            placeholder="e.g., What is the work experience? Tell me about the features...",
            key="question_input",
            label_visibility="visible"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Align button with input
        ask_clicked = st.button("🚀 Ask", type="primary", key="ask_btn")
    
    # Process question
    if ask_clicked and question.strip():
        with st.spinner("🤖 AI is thinking..."):
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
        st.warning("⚠️ Please enter a question before asking!")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Display chat history
if st.session_state.chat_history:
    st.markdown("## 📝 Chat History")
    
    # Clear all button at the top
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("🗑️ Clear All", key="clear_all", help="Clear entire chat history"):
            st.session_state.chat_history = []
            st.rerun()
    
    # Display chat messages
    for i, chat in enumerate(reversed(st.session_state.chat_history)):
        with st.container():
            st.markdown('<div style="border: 1px solid #e0e0e0; border-radius: 0.5rem; padding: 1rem; margin: 0.5rem 0; background-color: #fafafa;">', unsafe_allow_html=True)
            
            # Question
            st.markdown(f"**🤔 Question:** {chat['question']}")
            
            # Product info
            product_info = chat.get('product', 'Unknown')
            st.markdown(f"<small><em>📁 Product: {product_info}</em></small>", unsafe_allow_html=True)
            
            # Answer
            st.markdown(f"**🤖 Answer:**")
            st.markdown(chat['answer'])
            
            # Delete button
            col1, col2, col3 = st.columns([3, 1, 1])
            with col3:
                if st.button("🗑️", key=f"delete_{i}", help="Delete this conversation"):
                    st.session_state.chat_history.pop(-(i+1))
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
            
else:
    st.markdown("""
    <div style="text-align: center; padding: 2rem; color: #666;">
        <h3>💭 No conversations yet</h3>
        <p>Start asking questions about your documents to see the chat history here!</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #888; padding: 1rem;'>
        <p style='margin: 0; font-size: 0.9rem;'>
            🚀 Built with <strong>Streamlit</strong> • 
            ⚡ Powered by <strong>FastAPI</strong> • 
            🧠 Enhanced with <strong>OpenAI GPT-4</strong>
        </p>
        <p style='margin: 0.5rem 0 0 0; font-size: 0.8rem; color: #aaa;'>
            Multimodal RAG Pipeline for Intelligent Document Search
        </p>
    </div>
    """,
    unsafe_allow_html=True
) 