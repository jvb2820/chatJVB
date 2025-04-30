import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import CohereEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain_cohere import ChatCohere
import os
import base64
import io
from PIL import Image
import fitz  # PyMuPDF for PDF to image conversion
import docx  # python-docx for PDF to Word conversion

# Cohere API Key
COHERE_API_KEY = "aFR2rly7rpnQoOJ4Xxo1n6dAz4whPkemrnvztoA7"

# Set logo paths (adjust as needed)
CHATBOT_LOGO_PATH = os.path.join(os.path.dirname(__file__), "logo.jpg")  # Chatbot logo
USER_LOGO_PATH = os.path.join(os.path.dirname(__file__), "user_logo.svg")  # User logo

# Custom CSS for styling the chat messages
st.markdown("""
<style>
    .user-message {
        background-color: #123C5A;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
        display: flex;
        align-items: flex-start;

    }
    .bot-message {
        background-color: #0A1D37;
        padding: 10px;;
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
st.header("🚀 ChatJVB")

# Initialize session state for storing conversation history
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

# Create a container for chat history display
chat_container = st.container()

# PDF to Word conversion function
def convert_pdf_to_word(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    doc = docx.Document()
    
    for page_num in range(len(pdf_reader.pages)):
        text = pdf_reader.pages[page_num].extract_text()
        doc.add_paragraph(text)
    
    # Save to a BytesIO object
    docx_bytes = io.BytesIO()
    doc.save(docx_bytes)
    docx_bytes.seek(0)
    
    return docx_bytes

# PDF to Image conversion function
def convert_pdf_to_images(pdf_file):
    pdf_bytes = pdf_file.read()
    pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
    images = []
    
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
        img_bytes = pix.pil_tobytes(format="JPEG")
        img = Image.open(io.BytesIO(img_bytes))
        images.append(img)
    
    return images

# Sidebar for PDF conversion tools
with st.sidebar: 
    st.title("🔄 PDF Converter")
    
    pdf_file = st.file_uploader("Upload a PDF file to convert", type="pdf")
    
    if pdf_file is not None:
        # Conversion options
        conversion_type = st.radio(
            "Choose conversion type:",
            ("PDF to Word", "PDF to Images")
        )
        
        if st.button("Convert"):
            with st.spinner("Converting PDF..."):
                if conversion_type == "PDF to Word":
                    docx_bytes = convert_pdf_to_word(pdf_file)
                    st.download_button(
                        label="Download Word Document",
                        data=docx_bytes,
                        file_name=f"{pdf_file.name.split('.pdf')[0]}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                    st.success("Conversion complete! Click the download button above.")
                
                elif conversion_type == "PDF to Images":
                    images = convert_pdf_to_images(pdf_file)
                    st.success(f"Converted {len(images)} pages to images.")
                    
                    # Display and provide download for each image
                    for i, img in enumerate(images):
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.image(img, caption=f"Page {i+1}", use_column_width=True)
                        
                        with col2:
                            # Convert image to bytes for download
                            img_byte_arr = io.BytesIO()
                            img.save(img_byte_arr, format='PNG')
                            img_byte_arr.seek(0)
                            
                            st.download_button(
                                label="Download",
                                data=img_byte_arr,
                                file_name=f"page_{i+1}.png",
                                mime="image/png"
                            )
    
    # Add clear chat button in sidebar
    if st.button("Clear Chat History"):
        st.session_state.conversation_history = []
        st.rerun()
    
    # Add information about functionality
    st.markdown("---")
    st.write("**How to use:**")
    st.write("1. Chat with the assistant anytime")
    st.write("2. Convert PDFs to Word documents or images")

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
    
    # Generate response using Cohere (without PDF context)
    response = llm.invoke(user_question).content
    
    # Add response to history
    st.session_state.conversation_history.append({"role": "assistant", "content": response})
    
    # Force a rerun to update the display immediately and clear the input
    st.rerun()

# Load the logos (only once with better error handling)
if "chatbot_logo_base64" not in st.session_state or "user_logo_base64" not in st.session_state:
    try:
        # Load chatbot logo
        with open(CHATBOT_LOGO_PATH, "rb") as f:
            chatbot_logo_bytes = f.read()
            st.session_state.chatbot_logo_base64 = base64.b64encode(chatbot_logo_bytes).decode()

        # Load user logo
        with open(USER_LOGO_PATH, "rb") as f:
            user_logo_bytes = f.read()
            st.session_state.user_logo_base64 = base64.b64encode(user_logo_bytes).decode()
    except Exception as e:
        st.sidebar.warning(f"Could not load logos: {e}")
        # Set fallback empty strings for the logos
        st.session_state.chatbot_logo_base64 = ""
        st.session_state.user_logo_base64 = ""

# Display conversation history with custom styling
with chat_container:
    for message in st.session_state.conversation_history:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="message-container">
                <div class="user-message">
                    <div class="logo-container">
                        <img src="data:image/svg+xml;base64,{st.session_state.get('user_logo_base64', '')}" class="logo-image" alt="User Logo">
                    </div>
                     {message['content']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Display chatbot logo beside the text
            st.markdown(f"""
            <div class="message-container">
                <div class="bot-message">
                    <div class="logo-container">
                        <img src="data:image/png;base64,{st.session_state.get('chatbot_logo_base64', '')}" class="logo-image" alt="Chatbot Logo">
                    </div>
                    <div class="message-content">
                        {message['content']}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)