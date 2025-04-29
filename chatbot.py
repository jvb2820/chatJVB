import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import CohereEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain_cohere import ChatCohere
import os
import base64

# Cohere API Key
COHERE_API_KEY = "aFR2rly7rpnQoOJ4Xxo1n6dAz4whPkemrnvztoA7"

# Logo paths
BOT_LOGO_PATH = os.path.join(os.path.dirname(__file__), "logo.jpg")
USER_LOGO_PATH = os.path.join(os.path.dirname(__file__), "user_logo.svg")

st.markdown("""
<style>
    .user-message {
        background-color: #808080;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
        display: flex;
        align-items: flex-start;
    }
    .bot-message {
        background-color: #0000FF;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
        display: flex;
        align-items: flex-start;
    }
    .message-container {
        margin-bottom: 15px;
    }
    .logo-container {
        margin-right: 10px;
        flex-shrink: 0;
    }
    .logo-image {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        object-fit: cover;
    }
    .message-content {
        flex-grow: 1;
    }
</style>
""", unsafe_allow_html=True)

# App header
st.header("ChatJVB")

# Initialize session state for storing conversation history
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

# Create a container for chat history display
chat_container = st.container()

# Sidebar for document upload
with st.sidebar:
    st.title("Your Documents")
    file = st.file_uploader("Upload a PDF file to ask questions about it", type="pdf")
    
    
    if st.button("Clear Chat History"):
        st.session_state.conversation_history = []
        st.rerun()
    
    # Add information about functionality
    st.markdown("---")
    st.write("**How to use:**")
    st.write("1. Chat directly without a document")
    st.write("2. Or upload a PDF to ask questions about it")

# Process the file if uploaded
pdf_text = ""
vector_store = None

if file is not None:
    with st.spinner("Processing PDF..."):
        pdf_reader = PdfReader(file)
        for page in pdf_reader.pages:
            pdf_text += page.extract_text()

        # Break it into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            separators="\n",
            chunk_size=1000,
            chunk_overlap=150,
            length_function=len
        )
        chunks = text_splitter.split_text(pdf_text)

        # Generating embeddings with Cohere
        embeddings = CohereEmbeddings(
            cohere_api_key=COHERE_API_KEY,
            model="embed-english-v3.0",
            user_agent="langchain"
        )
        
        # Creating vector store - FAISS
        vector_store = FAISS.from_texts(chunks, embeddings)

# Define the LLM using Cohere
llm = ChatCohere(
    cohere_api_key=COHERE_API_KEY,
    temperature=0.2,
    max_tokens=1000,
    model="command"
)

# Use form to capture user input with auto-clearing functionality
with st.form(key="question_form", clear_on_submit=True):
    user_question = st.text_input("Type your question here")
    submit_button = st.form_submit_button("Send")

# Handle the user question
if submit_button and user_question:
    # Add user question to history
    st.session_state.conversation_history.append({"role": "user", "content": user_question})
    
    # Generate response based on whether a PDF is loaded
    if vector_store:
        # PDF-based Q&A
        match = vector_store.similarity_search(user_question)
        chain = load_qa_chain(llm, chain_type="stuff")
        response = chain.run(input_documents=match, question=user_question)
    else:
        # General chat without PDF context
        response = llm.invoke(user_question).content
    
    # Add response to history
    st.session_state.conversation_history.append({"role": "assistant", "content": response})
    
    # Force a rerun to update the display immediately and clear the input
    st.rerun()

# Load both logo images (only once with better error handling)
if "bot_logo_base64" not in st.session_state:
    try:
        with open(BOT_LOGO_PATH, "rb") as f:
            bot_logo_bytes = f.read()
            st.session_state.bot_logo_base64 = base64.b64encode(bot_logo_bytes).decode()
    except Exception as e:
        st.sidebar.warning(f"Could not load bot logo: {e}")
        # Set a fallback empty string for the logo
        st.session_state.bot_logo_base64 = ""

if "user_logo_base64" not in st.session_state:
    try:
        with open(USER_LOGO_PATH, "rb") as f:
            user_logo_bytes = f.read()
            st.session_state.user_logo_base64 = base64.b64encode(user_logo_bytes).decode()
    except Exception as e:
        st.sidebar.warning(f"Could not load user logo: {e}")
        # Set a fallback empty string for the logo
        st.session_state.user_logo_base64 = ""

# Display conversation history with custom styling
with chat_container:
    for message in st.session_state.conversation_history:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="message-container">
                <div class="user-message">
                    <div class="logo-container">
                        <img src="data:image/svg+xml;base64,{st.session_state.get('user_logo_base64', '')}" class="logo-image" alt="User">
                    </div>
                    <div class="message-content">
                         {message['content']}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Display logo beside the text
            st.markdown(f"""
            <div class="message-container">
                <div class="bot-message">
                    <div class="logo-container">
                        <img src="data:image/jpg;base64,{st.session_state.get('bot_logo_base64', '')}" class="logo-image" alt="Logo">
                    </div>
                    <div class="message-content">
                        {message['content']}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)