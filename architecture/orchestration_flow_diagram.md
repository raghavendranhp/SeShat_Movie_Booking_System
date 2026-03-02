# seshat ai orchestration flow diagram

this document maps the routing logic managed by the python orchestrator, showing how user inputs are parsed by agent 1 and then routed to the specialized agents alongside the local rag datasets.

```mermaid
graph TD
    %%user initiates request
    u[user input via streamlit] --> o[python orchestrator]
    
    %%orchestrator gets intent first
    o -->|raw text| a1[agent 1: intent classification]
    a1 -->|returns strict json| o
    
    %%orchestrator routes based on intent
    o -->|if intent == recommendation| a2[agent 2: recommendation]
    db1[(datasets/movies.json)] -.->|rag injection| a2
    
    o -->|if intent == book ticket| a3[agent 3: pricing]
    db2[(datasets/pricing_rules.json)] -.->|rag injection| a3
    
    o -->|analyze market| a4[agent 4: demand prediction]
    db3[(datasets/historical_sales.json)] -.->|rag injection| a4
    
    o -->|security check| a5[agent 5: fraud detection]
    
    %%agents return json to orchestrator
    a2 -->|json recommendations| o
    a3 -->|json calculated price| o
    a4 -->|json demand forecast| o
    a5 -->|json risk assessment| o
    
    %%orchestrator synthesizes final response
    o -->|formatted output & token count| ui[streamlit frontend]

```

## flow breakdown

1. user submits query to the python orchestrator.
2. orchestrator passes raw text to agent 1. agent 1 returns a json intent (e.g., "book ticket").
3. orchestrator reads the intent. if booking, it reads the requested movie and passes data to agent 3, agent 4, and agent 5 simultaneously.
4. specific local json datasets are injected into the agent prompts to ensure zero hallucination (rag simulation).
5. the orchestrator collects the json responses from all triggered agents, checks the risk score from agent 5, and delivers the final combined result back to the user interface.

