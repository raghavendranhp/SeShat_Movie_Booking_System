import logging
logging.getLogger("streamlit.runtime.scriptrunner_utils.script_run_context").setLevel(logging.ERROR)
import json
import os
import pandas as pd
import streamlit as st
from orchestrator import process_user_request

def setup_mock_memory():
    """initializes streamlit session state for headless batch processing."""
    #create blank memory state for the evaluation script
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "booking_context" not in st.session_state:
        st.session_state.booking_context = {
            "intent": None, "movie_name": None, "city": None, 
            "show_date": None, "num_tickets": None
        }
    if "total_tokens" not in st.session_state:
        st.session_state.total_tokens = 0
        st.session_state.prompt_tokens = 0
        st.session_state.completion_tokens = 0

def reset_context():
    """clears the booking context between each test scenario to prevent data leakage."""
    #reset memory for the next test
    st.session_state.booking_context = {
        "intent": None, "movie_name": None, "city": None, 
        "show_date": None, "num_tickets": None
    }

def run_evaluation():
    """reads test scenarios, processes them via agents, and exports results to csv."""
    setup_mock_memory()
    
    #load the test scenarios
    filepath = os.path.join("evaluation", "30_test_scenarios.json")
    try:
        with open(filepath, 'r') as file:
            scenarios = json.load(file)
    except filenotfounderror:
        print("error: 30_test_scenarios.json not found.")
        return

    results = []

    for idx, test in enumerate(scenarios):
        print(f"evaluating {idx + 1}/{len(scenarios)}: {test['scenario_id']}")
        
        #capture starting tokens
        start_tokens = st.session_state.total_tokens
        
        #process the request
        process_user_request(test['user_input'])
        
        #capture actual extracted intent from memory
        actual_intent = st.session_state.booking_context.get("intent", "unknown")
        
        #calculate tokens used for this specific turn
        tokens_used = st.session_state.total_tokens - start_tokens
        
        #determine if intent classification passed
        passed = (actual_intent == test['expected_intent'])
        
        #append to results list
        results.append({
            "scenario_id": test['scenario_id'],
            "category": test['category'],
            "user_input": test['user_input'],
            "expected_intent": test['expected_intent'],
            "actual_intent": actual_intent,
            "intent_match": passed,
            "tokens_consumed": tokens_used
        })
        
        reset_context()

    #convert to pandas dataframe and save to csv
    df = pd.DataFrame(results)
    output_path = os.path.join("evaluation", "evaluation_matrix.csv")
    df.to_csv(output_path, index=False)
    
    print(f"\n evaluation complete. results saved to {output_path}")
    print(f"overall accuracy: {df['intent_match'].mean() * 100:.2f}%")

if __name__ == "__main__":
    run_evaluation()