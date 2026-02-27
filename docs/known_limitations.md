# known limitations

while the seshat ai multi-agent movie booking system successfully demonstrates strict json formatting, intent routing, and zero-hallucination rag capabilities, there are several architectural and practical limitations in its current state.



## 1. dataset scaling and context window bottlenecks
the current rag (retrieval-augmented generation) implementation injects entire json files directly into the prompt payload. 
- **limitation:** this works flawlessly for a small mock dataset (10 movies, 5 theatres), but a real-world cinema database with thousands of showtimes, dynamic seat maps, and historical records would immediately exceed the context window limits of the llama 3 8b model.
- **future fix:** implementing a vector database (e.g., chroma or pinecone) or a semantic search layer to retrieve only the top-k most relevant json nodes before injecting them into the prompt.

## 2. multi-agent processing latency
because the architecture relies on discrete, specialized agents, processing a complex request (like booking a ticket) requires multiple api calls.
- **limitation:** the orchestrator must wait for agent 1 to classify the intent before firing requests to agent 3, 4, and 5. even when downstream agents run in parallel, the sequential bottleneck of the intent classification adds user-facing latency (typically 3-6 seconds per interaction).
- **future fix:** utilizing a smaller, faster local model specifically fine-tuned for sequence classification (like bert) to handle intent routing in milliseconds, reserving the heavier llm for reasoning tasks.

## 3. hardcoded orchestrator routing
the python `orchestrator.py` uses rigid `if/elif` statements based on the exact string output of agent 1.
- **limitation:** the system is not a truly autonomous agentic framework (like autogen or crewai). the agents cannot dynamically decide to talk to each other to solve a problem; they only communicate directly with the central python script. as seen in the evaluation matrix, if agent 1 classifies booking 100 tickets as `bulk/corporate booking` instead of `book ticket`, the python logic entirely bypasses the fraud detection agent.
- **future fix:** implementing a dynamic router or a graph-based state machine (like langgraph) where the fraud agent is a middleware layer that evaluates all outgoing transactional intents.

## 4. ephemeral state management
conversational memory is handled entirely within streamlit's `st.session_state`.
- **limitation:** if the user refreshes the browser, the memory is completely wiped. the llm has no persistent memory of the user's past bookings, preferences, or previous session risk scores. furthermore, updating the context dictionary relies on agent 1 consistently extracting entities perfectly.
- **future fix:** integrating a persistent database (like postgresql or redis) attached to user session ids to store long-term context and risk profiles.

## 5. vulnerability to prompt injection
despite the strong system guardrails and the dedicated fraud agent (agent 5), llms are inherently susceptible to adversarial attacks.
- **limitation:** a highly sophisticated prompt injection could theoretically trick agent 1 into misclassifying an intent, or confuse agent 3 (pricing) into applying negative multipliers, bypassing the zero-temperature json strictness.