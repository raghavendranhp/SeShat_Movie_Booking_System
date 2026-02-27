import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
#initialize groq client securely
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def call_llm(system_prompt, user_input):
    """
    executes an api call to groq using the llama3-8b model.
    enforces a temperature of 0.0 for strict json compliance and 
    updates streamlit session state with token usage metrics.
    """
    #construct message payload
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]
    
    #call the model
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=0.0,
        max_tokens=1024,
        response_format={"type": "json_object"}
    )
    
    #parse the response content
    generated_text = response.choices[0].message.content
    
    #extract token usage data
    usage = response.usage
    
    #update global token counters in ui
    if "prompt_tokens" in st.session_state:
        st.session_state.prompt_tokens += usage.prompt_tokens
        st.session_state.completion_tokens += usage.completion_tokens
        st.session_state.total_tokens += usage.total_tokens
        
    return generated_text