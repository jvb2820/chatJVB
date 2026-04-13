import streamlit as st
from langchain_cohere import ChatCohere
import os
import base64
import re

# Cohere API Key
# Use st.secrets in production!
COHERE_API_KEY = "aFR2rly7rpnQoOJ4Xxo1n6dAz4whPkemrnvztoA7"

# Set logo paths
CHATBOT_LOGO_PATH = os.path.join(os.path.dirname(__file__), "logo.jpg")
USER_LOGO_PATH = os.path.join(os.path.dirname(__file__), "user_logo.svg")

# Pre-defined responses for specific questions
PRE_DEFINED_RESPONSES = {
    "who is jvb": "JVB is Jeuz Vinci Bas, my creator. He is a talented programmer and software developer. You can connect with him on LinkedIn at https://www.linkedin.com/in/jeuz-vinci-bas-b51639341/. He specializes in AI applications and software development.",
    "what is jvb": "JVB stands for Jeuz Vinci Bas, the developer who created me. He's a programmer with expertise in AI and software development. Feel free to connect with him on LinkedIn at https://www.linkedin.com/in/jeuz-vinci-bas-b51639341/.",
    "tell me about jvb": "Jeuz Vinci Bas (JVB) is a programmer and developer who created me. He works on various software projects including AI applications like this chatbot. You can learn more about his work or connect with him on LinkedIn at https://www.linkedin.com/in/jeuz-vinci-bas-b51639341/.",
    "jvb": "JVB refers to Jeuz Vinci Bas, my creator and a software developer. He built this chatbot as part of his work in AI development. You can connect with him on LinkedIn at https://www.linkedin.com/in/jeuz-vinci-bas-b51639341/ if you'd like to learn more about his projects.",
    "who created you": "I was created by Jeuz Vinci Bas (JVB), a programmer and AI developer. This chatbot is one of his projects combining AI conversation capabilities.",
    "who is jeuz": "Jeuz Vinci Bas is my creator. He is a talented programmer and software developer with expertise in AI applications. You can connect with him on LinkedIn at https://www.linkedin.com/in/jeuz-vinci-bas-b51639341/.",
    "who is jeuz vinci bas": "Jeuz Vinci Bas is my creator and developer. He specializes in AI applications and software development, including this chatbot. You can learn more about his work or connect with him on LinkedIn at https://www.linkedin.com/in/jeuz-vinci-bas-b51639341/.",
    "tell me about jeuz": "Jeuz Vinci Bas is the developer who created me. He works on various software projects with a focus on AI applications. You can connect with him on LinkedIn at https://www.linkedin.com/in/jeuz-vinci-bas-b51639341/ to learn more about his work.",
    "tell me about jeuz vinci bas": "Jeuz Vinci Bas is a programmer and AI developer who created this chatbot. He combines AI conversation capabilities with professional expertise. You can connect with him on LinkedIn at https://www.linkedin.com/in/jeuz-vinci-bas-b51639341/.",
    "jeuz": "Jeuz refers to Jeuz Vinci Bas, my creator and a software developer. He built this chatbot as part of his work in AI development. You can connect with him on LinkedIn at https://www.linkedin.com/in/jeuz-vinci-bas-b51639341/.",
    "jeuz vinci bas": "Jeuz Vinci Bas is my creator and a talented software developer specializing in AI applications. This chatbot is one of his projects. You can connect with him on LinkedIn at https://www.linkedin.com/in/jeuz-vinci-bas-b51639341/."
}

def get_predefined_response(question):
    question_lower = question.lower().strip()
    if question_lower in PRE_DEFINED_RESPONSES:
        return PRE_DEFINED_RESPONSES[question_lower]
    
    normalized_question = re.sub(r'[^\w\s]', '', question_lower)
    normalized_question_words = set(normalized_question.split())
    
    if ('who' in normalized_question_words and 'jeuz' in normalized_question_words) or \
       ('tell' in normalized_question_words and 'about' in normalized_question_words and 'jeuz' in normalized_question_words) or \
       ('jeuz' in normalized_question_words and len(normalized_question_words) <= 3):
        return PRE_DEFINED_RESPONSES.get("who is jeuz")
    
    if ('who' in normalized_question_words and 'jvb' in normalized_question_words) or \
       ('tell' in normalized_question_words and 'about' in normalized_question_words and 'jvb' in normalized_question_words) or \
       ('jvb' in normalized_question_words and len(normalized_question_words) <= 3):
        return PRE_DEFINED_RESPONSES.get("who is jvb")
    
    for key, response in PRE_DEFINED_RESPONSES.items():
        key_words = set(key.split())
        if key_words.issubset(normalized_question_words):
            return response
            
    return None

# Custom CSS for modern chatbot styling
st.set_page_config(page_title="ChatJVB", page_icon="🚀", layout="centered")

st.markdown("""
<style>
    .user-message {
        background-color: #123C5A;
        padding: 12px 16px;
        border-radius: 15px 15px 0 15px;
        margin-bottom: 10px;
        color: white;
        max-width: 80%;
        margin-left: auto;
    }
    .bot-message {
        background-color: #0A1D37;
        padding: 12px 16px;
        border-radius: 15px 15px 15px 0;
        margin-bottom: 10px;
        color: white;
        max-width: 80%;
        display: flex;
        align-items: flex-start;
    }
    .logo-container {
        margin-right: 12px;
        flex-shrink: 0;
    }
    .logo-image {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        object-fit: cover;
        border: 1px solid #1E3A8A;
    }
    .message-content {
        line-height: 1.5;
    }
    .stTextInput > div > div > input {
        border-radius: 20px;
    }
</style>
""", unsafe_allow_html=True)

# App Title
st.title("🚀 ChatJVB")
st.caption("Your professional AI assistant created by Jeuz Vinci Bas")

# Initialize session state
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

if "chatbot_logo_base64" not in st.session_state:
    try:
        if os.path.exists(CHATBOT_LOGO_PATH):
            with open(CHATBOT_LOGO_PATH, "rb") as f:
                st.session_state.chatbot_logo_base64 = base64.b64encode(f.read()).decode()
        else:
            st.session_state.chatbot_logo_base64 = ""
            
        if os.path.exists(USER_LOGO_PATH):
            with open(USER_LOGO_PATH, "rb") as f:
                st.session_state.user_logo_base64 = base64.b64encode(f.read()).decode()
        else:
            st.session_state.user_logo_base64 = ""
    except Exception:
        st.session_state.chatbot_logo_base64 = ""
        st.session_state.user_logo_base64 = ""

# Chat history container
chat_container = st.container()

# Display chat history
with chat_container:
    for message in st.session_state.conversation_history:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="user-message">
                {message['content']}
            </div>
            """, unsafe_allow_html=True)
        else:
            logo_html = ""
            if st.session_state.chatbot_logo_base64:
                logo_html = f'<div class="logo-container"><img src="data:image/jpeg;base64,{st.session_state.chatbot_logo_base64}" class="logo-image"></div>'
            
            st.markdown(f"""
            <div class="bot-message">
                {logo_html}
                <div class="message-content">{message['content']}</div>
            </div>
            """, unsafe_allow_html=True)

# Define the LLM
llm = ChatCohere(
    cohere_api_key=COHERE_API_KEY,
    temperature=0.3,
    max_tokens=1000,
    model="command"
)

# User input form
with st.form(key="chat_form", clear_on_submit=True):
    col1, col2 = st.columns([8, 1])
    with col1:
        user_input = st.text_input("Message ChatJVB...", placeholder="Ask me anything...", label_visibility="collapsed")
    with col2:
        submit = st.form_submit_button("Send")

if submit and user_input:
    st.session_state.conversation_history.append({"role": "user", "content": user_input})
    
    predefined = get_predefined_response(user_input)
    if predefined:
        response = predefined
    else:
        with st.spinner("Thinking..."):
            try:
                response = llm.invoke(user_input).content
            except Exception as e:
                response = f"Sorry, I encountered an error: {str(e)}"
    
    st.session_state.conversation_history.append({"role": "assistant", "content": response})
    st.rerun()

# Sidebar for utilities
with st.sidebar:
    st.image(CHATBOT_LOGO_PATH if os.path.exists(CHATBOT_LOGO_PATH) else None, width=100)
    st.title("ChatJVB")
    st.write("A lightweight chatbot powered by Cohere AI.")
    
    if st.button("Clear Chat History", use_container_width=True):
        st.session_state.conversation_history = []
        st.rerun()
    
    st.divider()
    st.write("Created by **Jeuz Vinci Bas**")
    st.write("[LinkedIn](https://www.linkedin.com/in/jeuz-vinci-bas-b51639341/)")
