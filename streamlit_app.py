import streamlit as st
import requests
import os

# Configure the page
st.set_page_config(
    page_title="Multimodal RAG Assistant",
    page_icon="📚",
    layout="wide"
)

# Title and description
st.title("📚 Multimodal RAG Assistant")
st.markdown("Upload a PDF document and ask questions about it using AI-powered retrieval and generation.")

# Initialize session state
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Sidebar for file upload
with st.sidebar:
    st.header("📄 Document Upload")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload a PDF document to analyze"
    )
    
    if uploaded_file is not None:
        # Save the uploaded file temporarily
        with open("temp_upload.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Upload to backend
        try:
            with open("temp_upload.pdf", "rb") as f:
                files = {"file": f}
                response = requests.post("http://localhost:8000/upload", files=files)
                
            if response.status_code == 200:
                st.success("✅ Document uploaded successfully!")
                st.session_state.uploaded_file = uploaded_file.name
                # Clear chat history when new document is uploaded
                st.session_state.chat_history = []
            else:
                st.error(f"❌ Upload failed: {response.text}")
                
        except Exception as e:
            st.error(f"❌ Error uploading file: {str(e)}")
        finally:
            # Clean up temporary file
            if os.path.exists("temp_upload.pdf"):
                os.remove("temp_upload.pdf")
    
    # Display current document
    if st.session_state.uploaded_file:
        st.info(f"📄 Current document: {st.session_state.uploaded_file}")

# Main chat interface
st.header("💬 Ask Questions")

# Check if document is uploaded
if not st.session_state.uploaded_file:
    st.warning("⚠️ Please upload a PDF document first using the sidebar.")
    st.stop()

# Question input
question = st.text_input(
    "Ask a question about your document:",
    placeholder="e.g., What does figure 3-1 show?",
    key="question_input"
)

# Ask button
if st.button("🤔 Ask Question", type="primary"):
    if question.strip():
        with st.spinner("🤖 Thinking..."):
            try:
                response = requests.post(
                    "http://localhost:8000/rag/query",
                    json={"question": question}
                )
                
                if response.status_code == 200:
                    answer = response.json()["answer"]
                    
                    # Add to chat history
                    st.session_state.chat_history.append({
                        "question": question,
                        "answer": answer
                    })
                    
                    # Clear the input
                    st.session_state.question_input = ""
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
            
            # Add a delete button for each chat
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