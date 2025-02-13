import streamlit as st
import requests
import os

st.set_page_config(page_title="Smart PDF Q&A Bot", page_icon="📄", layout="wide")

# Custom CSS for an enhanced gradient UI
st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460);
            color: white;
        }
        .stChatMessage {
            padding: 15px;
            border-radius: 12px;
            margin: 10px 0;
            max-width: 75%;
            word-wrap: break-word;
            font-size: 16px;
            font-weight: 500;
        }
        .user {
            background: linear-gradient(135deg, #00c6ff, #0072ff);
            color: white;
            align-self: flex-end;
        }
        .assistant {
            background: linear-gradient(135deg, #ff416c, #ff4b2b);
            color: white;
            align-self: flex-start;
        }
        .message-container {
            display: flex;
            flex-direction: column;
            gap: 10px;
            max-height: 65vh;
            overflow-y: auto;
            padding-bottom: 100px; 
        }
        .title-container {
            text-align: center;
            font-size: 28px;
            font-weight: bold;
            background: linear-gradient(135deg, #ff8c00, #ff2e63);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .intro-container {
            text-align: center;
            font-size: 18px;
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
        }
        .upload-container {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            padding: 15px;
            border-top: 2px solid #ff2e63;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(10px);
            text-align: center;
        }
    </style>
    """,
    unsafe_allow_html=True
)
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

st.markdown('<h1 class="title-container">💬 Smart PDF Q&A Bot</h1>', unsafe_allow_html=True)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history inside a scrollable container
st.markdown('<div class="message-container">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    role_class = "user" if msg["role"] == "user" else "assistant"
    st.markdown(f'<div class="stChatMessage {role_class}">{msg["content"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Introduction section
st.markdown(
    """
    <div class="intro-container">
        📜 <b>Welcome to Smart PDF Q&A Bot!</b><br>
        Upload a PDF, and ask questions about its content. Our AI will read and answer your queries. 
        Try it now by uploading a document below!
    </div>
    """,
    unsafe_allow_html=True
)

# File uploader - Fixed at bottom with gradient effect
st.markdown('<div class="upload-container">', unsafe_allow_html=True)
uploaded_file = st.file_uploader("📂 Upload a PDF to begin", type="pdf")
st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file and "pdf_processed" not in st.session_state:
    with st.spinner("📤 Uploading and processing PDF..."):
        files = {"file": uploaded_file.getvalue()}
        response = requests.post(f"{BACKEND_URL}/process/", files=files)
        if response.status_code == 200:
            st.session_state.pdf_processed = True
            st.success("✅ PDF processed! Ask your questions above.")
        else:
            st.error("❌ Failed to process PDF.")


# Chat input field
if st.session_state.get("pdf_processed", False):
    query = st.chat_input("💡 Ask something about the PDF...")
    if query:
        # Display user message
        st.session_state.messages.append({"role": "user", "content": query})
        st.markdown(f'<div class="stChatMessage user">{query}</div>', unsafe_allow_html=True)

        # Get AI response
        with st.spinner("🤖 Thinking..."):
            response = requests.post(f"{BACKEND_URL}/ask/", params={"query": query})
            answer = response.json().get("answer", "❌ Error fetching answer.")


        # Display assistant message
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.markdown(f'<div class="stChatMessage assistant">{answer}</div>', unsafe_allow_html=True)
