import streamlit as st
from orchestrator import process_user_request

def initialize_session_state():
    """initializes all required session state variables for memory and token tracking."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "booking_context" not in st.session_state:
        st.session_state.booking_context = {
            "intent": None,
            "movie_name": None,
            "city": None,
            "show_date": None,
            "num_tickets": None
        }
        
    if "total_tokens" not in st.session_state:
        st.session_state.total_tokens = 0
    if "prompt_tokens" not in st.session_state:
        st.session_state.prompt_tokens = 0
    if "completion_tokens" not in st.session_state:
        st.session_state.completion_tokens = 0

def render_sidebar():
    """renders the sidebar displaying real-time token usage metrics."""
    st.sidebar.title("token usage")
    st.sidebar.metric(label="total tokens", value=st.session_state.total_tokens)
    st.sidebar.metric(label="prompt tokens", value=st.session_state.prompt_tokens)
    st.sidebar.metric(label="completion tokens", value=st.session_state.completion_tokens)
    
    #display current extracted context for debugging
    st.sidebar.title("current context")
    st.sidebar.json(st.session_state.booking_context)

def render_chat_history():
    """iterates through session state and renders the chat history in the ui."""
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def main():
    """main execution function for the streamlit application."""
    st.set_page_config(page_title="seshat ai movie booking", layout="wide")
    st.title("seshat ai movie booking")
    
    initialize_session_state()
    render_sidebar()
    render_chat_history()
    
    user_input = st.chat_input("how can i help you with your movie booking today?")
    
    if user_input:
        #append and render user message
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
            
        #process request through the python orchestrator
        with st.spinner("processing request via multi-agent system..."):
            assistant_response = process_user_request(user_input)
            
        #append and render assistant message
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})
        with st.chat_message("assistant"):
            st.markdown(assistant_response)
            
        #refresh ui to update sidebar token metrics
        st.rerun()

if __name__ == "__main__":
    main()