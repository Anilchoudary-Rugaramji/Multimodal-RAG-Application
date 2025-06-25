import streamlit as st
import requests
import os

# Configure the page
st.set_page_config(
    page_title="Multimodal RAG Assistant",
    page_icon="📚",
    layout="wide"
)

API_BASE = "http://localhost:8001"  # Update if backend runs elsewhere
ADMIN_PASSWORD = "admin123"  # Change this to your desired password

# Title and description
st.title("📚 Multimodal RAG Assistant")
st.markdown("Select a product and ask questions about its documents using AI-powered retrieval and generation.")

# Initialize session state
if 'selected_product' not in st.session_state:
    st.session_state.selected_product = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'admin_authenticated' not in st.session_state:
    st.session_state.admin_authenticated = False

# Admin Authentication
with st.sidebar:
    st.header("🔐 Admin Access")
    admin_password = st.text_input("Admin Password", type="password", key="admin_pwd")
    if st.button("Login as Admin"):
        if admin_password == ADMIN_PASSWORD:
            st.session_state.admin_authenticated = True
            st.success("✅ Admin access granted!")
            st.rerun()
        else:
            st.error("❌ Invalid password!")
    
    if st.session_state.admin_authenticated:
        if st.button("Logout"):
            st.session_state.admin_authenticated = False
            st.rerun()
        st.success("🔓 Admin Mode Active")

# Admin Upload Section (only visible when authenticated)
if st.session_state.admin_authenticated:
    st.header("📤 Admin Document Upload")
    
    # Product input for upload
    upload_product = st.text_input("Product Name (e.g., Product1, Product2)", key="upload_product")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a PDF file to upload",
        type=['pdf'],
        help="Upload a PDF document for the selected product"
    )
    
    if uploaded_file is not None and upload_product:
        if st.button("Upload Document", type="primary"):
            with st.spinner("Uploading and processing document..."):
                try:
                    # Read file into memory
                    file_bytes = uploaded_file.getvalue()
                    
                    # Upload to backend
                    files = {"file": (uploaded_file.name, file_bytes)}
                    headers = {"x-api-key": "secret123"}  # Use your actual API key
                    
                    response = requests.post(
                        f"{API_BASE}/admin/upload",
                        files=files,
                        headers=headers,
                        params={"product": upload_product}
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"✅ Document uploaded successfully!")
                        st.info(f"Product: {result['product']}")
                        st.info(f"Filename: {result['filename']}")
                        st.info(f"Chunks stored: {result['chunks_stored']}")
                        # Clear the upload
                        st.rerun()
                    else:
                        st.error(f"❌ Upload failed: {response.text}")
                        
                except Exception as e:
                    st.error(f"❌ Error uploading file: {str(e)}")

# Sidebar for product and document selection (for all users)
with st.sidebar:
    st.header("🗂️ Product Selection")
    # Fetch available products and documents from backend
    try:
        resp = requests.get(f"{API_BASE}/products")
        if resp.status_code == 200:
            products_data = resp.json()
            products = list(products_data.keys())
        else:
            st.error("Failed to fetch products.")
            products = []
            products_data = {}
    except Exception as e:
        st.error(f"Error connecting to backend: {str(e)}")
        products = []
        products_data = {}

    if products:
        product = st.selectbox("Select a product:", products, index=0 if st.session_state.selected_product is None else products.index(st.session_state.selected_product))
        st.session_state.selected_product = product
        # Show documents for the selected product
        docs = products_data.get(product, [])
        if docs:
            st.info(f"Documents for {product}:\n" + "\n".join(docs))
        else:
            st.warning(f"No documents uploaded for {product}.")
    else:
        st.warning("No products available.")

# Main chat interface
st.header("💬 Ask Questions")

# Check if product is selected and has documents
if not st.session_state.selected_product or not products_data.get(st.session_state.selected_product):
    st.warning("⚠️ Please select a product with uploaded documents using the sidebar.")
    st.stop()

# Question input
question = st.text_input(
    "Ask a question about your selected product:",
    placeholder="e.g., What does figure 3-1 show?",
    key="question_input"
)

# Ask button
if st.button("🤔 Ask Question", type="primary"):
    if question.strip():
        with st.spinner("🤖 Thinking..."):
            try:
                response = requests.post(
                    f"{API_BASE}/rag/query",
                    json={"question": question, "product": st.session_state.selected_product}
                )
                print("QUERY RESPONSE:", response.status_code, response.text)
                if response.status_code == 200:
                    answer = response.json()["answer"]
                    # Add to chat history
                    st.session_state.chat_history.append({
                        "question": question,
                        "answer": answer
                    })
                    # Clear the input
                    st.rerun()
                else:
                    st.error(f"❌ Error: {response.text}")
            except Exception as e:
                st.error(f"❌ Error connecting to backend: {str(e)}")

# Display chat history
if st.session_state.chat_history:
    st.header("📝 Chat History")
    for i, chat in enumerate(reversed(st.session_state.chat_history)):
        with st.expander(f"Q: {chat['question'][:50]}...", expanded=True):
            st.markdown(f"**Question:** {chat['question']}")
            st.markdown(f"**Answer:** {chat['answer']}")
            if st.button(f"🗑️ Delete", key=f"delete_{i}"):
                st.session_state.chat_history.pop(-(i+1))
                st.rerun()

# Clear chat history button
if st.session_state.chat_history:
    if st.button("🗑️ Clear All History"):
        st.session_state.chat_history = []
        st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>Built with Streamlit • Powered by FastAPI • Multimodal RAG Pipeline</p>
    </div>
    """,
    unsafe_allow_html=True
) 