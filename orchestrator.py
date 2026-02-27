import json
import os
import streamlit as st
from groq_client import call_llm

def load_json_file(filepath):
    """loads and returns a json dataset from the specified filepath."""
    try:
        with open(filepath, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def read_prompt(filename):
    """reads and returns the content of a text prompt file."""
    filepath = os.path.join("prompts", filename)
    try:
        with open(filepath, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return ""

def update_context(extracted_data):
    """updates the global booking context in streamlit session state."""
    for key in st.session_state.booking_context.keys():
        if key in extracted_data and extracted_data[key]:
            st.session_state.booking_context[key] = extracted_data[key]

def process_user_request(user_input):
    """main orchestration logic routing the user input to appropriate agents and datasets."""
    #load required system prompts
    system_prompt = read_prompt("system_prompt.txt")
    agent_1_prompt = read_prompt("agent_1_intent.txt")
    
    #call agent 1 for intent classification
    context_str = json.dumps(st.session_state.booking_context)
    combined_prompt_1 = f"{system_prompt}\n\n{agent_1_prompt}\n\ncurrent context: {context_str}"
    
    agent_1_response = call_llm(combined_prompt_1, user_input)
    
    try:
        intent_data = json.loads(agent_1_response)
        update_context(intent_data)
        current_intent = intent_data.get("intent", "unknown")
    except json.JSONDecodeError:
        return "system error: agent 1 failed to return strict json."

    #route 1: recommendations (uses movies.json)
    if current_intent == "movie recommendation":
        movies_db = load_json_file(os.path.join("datasets", "movies.json"))
        agent_2_prompt = read_prompt("agent_2_recommendation.txt")
        combined_prompt_2 = f"{system_prompt}\n\n{agent_2_prompt}\n\ndataset: {json.dumps(movies_db)}"
        
        agent_2_response = call_llm(combined_prompt_2, user_input)
        
        try:
            rec_data = json.loads(agent_2_response)
            if "this information is not available" in str(rec_data).lower():
                return "this information is not available in the current cinema policy dataset."
            
            movies = rec_data.get("recommended_movies", [])
            response_text = "here are my top recommendations based on your preferences:\n"
            for m in movies:
                response_text += f"- **{m.get('title')}** ({m.get('genre')}, {m.get('language')}) - match score: {m.get('match_score')}\n"
            return response_text
        except json.JSONDecodeError:
            return "system error: agent 2 failed to return strict json."

    #route 2: booking (uses pricing_rules, historical_sales, and discount_campaigns)
    elif current_intent == "book ticket":
        ctx = st.session_state.booking_context
        if not ctx.get("movie_name") or not ctx.get("show_date") or not ctx.get("num_tickets"):
            return "i can help with that. could you please provide the movie name, date, and number of tickets?"

        pricing_db = load_json_file(os.path.join("datasets", "pricing_rules.json"))
        sales_db = load_json_file(os.path.join("datasets", "historical_sales.json"))
        discounts_db = load_json_file(os.path.join("datasets", "discount_campaigns.json"))
        
        #agent 5 (fraud) uses the discounts database to check for promo abuse
        agent_5_prompt = read_prompt("agent_5_fraud.txt")
        combined_prompt_5 = f"{system_prompt}\n\n{agent_5_prompt}\n\ndiscounts dataset: {json.dumps(discounts_db)}\nuser context: booking {ctx.get('num_tickets')} tickets for {ctx.get('movie_name')}"
        fraud_response = call_llm(combined_prompt_5, user_input)
        
        try:
            fraud_data = json.loads(fraud_response)
            if fraud_data.get("risk_category") == "high":
                return f"security alert: transaction blocked. reason: {fraud_data.get('recommended_action')}"
        except json.JSONDecodeError:
            pass 

        #agent 3 (pricing) uses both pricing rules and discounts databases
        agent_3_prompt = read_prompt("agent_3_pricing.txt")
        combined_prompt_3 = f"{system_prompt}\n\n{agent_3_prompt}\n\npricing dataset: {json.dumps(pricing_db)}\ndiscounts dataset: {json.dumps(discounts_db)}\nbooking details: {json.dumps(ctx)}"
        pricing_response = call_llm(combined_prompt_3, user_input)
        
        try:
            price_data = json.loads(pricing_response)
            final_price = price_data.get("final_ticket_price", "unknown")
            reasoning = price_data.get("pricing_reasoning", "")
        except json.JSONDecodeError:
            final_price = "error calculating price"
            reasoning = ""

        #agent 4 (demand) uses the historical sales database
        agent_4_prompt = read_prompt("agent_4_demand.txt")
        combined_prompt_4 = f"{system_prompt}\n\n{agent_4_prompt}\n\nhistorical sales: {json.dumps(sales_db)}\nbooking details: {json.dumps(ctx)}"
        demand_response = call_llm(combined_prompt_4, user_input)
        
        try:
            demand_data = json.loads(demand_response)
            predicted_demand = demand_data.get("predicted_demand", "unknown")
        except json.JSONDecodeError:
            predicted_demand = "unknown"

        return f"booking initiated for {ctx.get('num_tickets')} tickets to see {ctx.get('movie_name')} on {ctx.get('show_date')}.\n\n**final price:** {final_price}\n**pricing logic:** {reasoning}\n**predicted demand:** {predicted_demand}."

    #route 3: cancellations (uses cancellation_policies.json)
    elif current_intent in ["cancel ticket", "refund status"]:
        cancellation_db = load_json_file(os.path.join("datasets", "cancellation_policies.json"))
        return f"i can help you with your {current_intent}. according to our policy:\n\n```json\n{json.dumps(cancellation_db, indent=2)}\n```\n\nwould you like to proceed with this action?"

    #route 4: theatre timings (uses theatres.json)
    elif current_intent == "check show timings":
        theatres_db = load_json_file(os.path.join("datasets", "theatres.json"))
        ctx = st.session_state.booking_context
        if not ctx.get("movie_name"):
            return "which movie would you like to check timings for?"
        return f"here is the current theatre and showtime data for {ctx.get('movie_name')}:\n\n```json\n{json.dumps(theatres_db, indent=2)}\n```\n\nlet me know which showtime works best for you."

    #route 5: bulk logic
    elif current_intent == "bulk/corporate booking":
        return "for bulk bookings of 20+ tickets, please contact our corporate sales team directly at corporate@seshatai.com to access special event tiers and discounts."

    #fallback
    else:
        return "i couldn't quite understand your request. could you please clarify if you want to book a ticket, get recommendations, or check a refund?"