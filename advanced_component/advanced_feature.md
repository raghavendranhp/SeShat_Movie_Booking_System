# advanced feature: dynamic graph-based orchestration



## overview
while the current seshat ai implementation relies on a static python orchestrator using rigid `if/elif` logic to route user intents, the next evolution of the platform integrates a dynamic, graph-based state machine (e.g., langgraph). this advanced component transforms the system from a simple sequential router into a truly autonomous agentic network.

## core concepts

### 1. the global state object
instead of relying solely on streamlit's ephemeral session state, the graph architecture introduces a persistent, typed `state` object. this object flows through the graph, being appended to (not overwritten) by each agent. it tracks the entire conversation history, extracted entities, intermediate reasoning steps, and risk scores.

### 2. nodes (agents) as functions
each of the 5 existing agents becomes a discrete node in the graph. when a node is activated, it receives the current state, executes its specific llm prompt (with optimized local rag injection), and returns a state update containing its strictly formatted json output.

### 3. conditional edges (dynamic routing)
the rigid python logic is replaced by conditional edges driven by the state's data. 
- for example, after agent 1 classifies the intent as "book ticket", a conditional edge evaluates the state. 
- if `num_tickets` is missing, the edge dynamically routes the flow back to a "human-in-the-loop" node to ask the user for clarification, bypassing the rest of the agent chain.
- if the fraud agent (agent 5) flags a transaction as high risk, it can dynamically route the state to a "human escalation" node instead of abruptly blocking the user.

## architectural benefits

- **cyclical reasoning:** agents can now converse with each other. if agent 3 (pricing) calculates a surge that exceeds a user's previously stated budget, it can route the state back to agent 2 (recommendation) to automatically find a cheaper alternative before responding to the user.
- **scalability:** adding a new agent (e.g., agent 6: food & beverage pre-ordering) simply requires defining a new node and updating the edge routing conditions, without rewriting the core orchestrator logic.
- **fault tolerance:** if an agent returns malformed json, the graph can automatically route the state to a "self-correction" node to prompt the llm to fix its own formatting error without crashing the application.