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

# Title and description
st.title("📚 Multimodal RAG Assistant")
st.markdown("Select a product and ask questions about its documents using AI-powered retrieval and generation.")

# Initialize session state
if 'selected_product' not in st.session_state:
    st.session_state.selected_product = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Sidebar for product and document selection
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