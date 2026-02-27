
# memory state design

this document outlines how the seshat ai orchestrator maintains conversational context across multiple turns using streamlit's session state. because the system routes isolated requests to different stateless agents, a centralized memory manager is strictly required.



## core memory structure

the memory state is a continuous dictionary stored in `st.session_state`. it captures the raw dialogue, the extracted intents from agent 1, and the cumulative token usage for performance evaluation.

```python
def initialize_memory():
    """initializes the session state variables for chat history and context."""
    if "chat_history" not in st.session_state:
        #stores full conversation history for the ui
        st.session_state.chat_history = []
        
    if "current_booking_context" not in st.session_state:
        #stores active transaction details extracted by agent 1
        st.session_state.current_booking_context = {
            "intent": None,
            "movie_name": None,
            "city": None,
            "show_date": None,
            "num_tickets": None,
            "risk_score": 0
        }

```

## memory update lifecycle

1. user input: the user submits a query. the text is appended to `st.session_state.chat_history` as a "user" role message.
2. intent extraction (agent 1): the orchestrator sends the raw text to agent 1. agent 1 returns a structured json.
3. context mutation: the orchestrator parses the json and updates `st.session_state.current_booking_context`. if a user says "i want two tickets for supernova crash", those specific fields are updated while preserving past context (e.g., if they previously specified "mumbai").
4. context injection: when calling downstream agents (agent 2, 3, 4, 5), the orchestrator serializes the `current_booking_context` and injects it into the prompt alongside the rag datasets. this allows agent 3 to calculate pricing without asking the user for the movie name again.
5. ai response: the final aggregated system response is appended to `st.session_state.chat_history` as an "assistant" role message.

## memory constraints and limitations

* token limits: to prevent the context window from overflowing during long interactions, only the `current_booking_context` and the last 5 turns of `chat_history` are sent to the groq api for conversational grounding.
* session reset: the memory state is completely volatile. refreshing the streamlit browser tab flushes the memory, simulating a new user session and resetting the fraud risk score.


