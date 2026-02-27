# failure handling and fallback mechanisms



a robust multi-agent system must anticipate and gracefully recover from both user-driven errors and llm-driven anomalies. the seshat ai architecture implements several layers of failure handling to ensure system stability and strict policy adherence.

## 1. strict json parsing failures
even with the groq api `response_format={"type": "json_object"}` and a temperature of 0.0, there is a non-zero chance of malformed outputs.
- **the risk:** an agent returns a truncated response or invalid json syntax, which would normally crash the python application.
- **the fallback:** the `orchestrator.py` wraps every single `json.loads()` call in a `try/except json.jsondecodeerror` block. if an agent fails to return parseable json, the system intercepts the error and returns a safe, hardcoded string to the ui (e.g., "system error: agent 1 failed to return strict json."), preventing a total application crash.

## 2. zero-hallucination and out-of-domain queries
users will inevitably ask for movies, theatres, or pricing rules that do not exist in the injected json datasets.
- **the risk:** the llm attempts to please the user by hallucinating real-world knowledge (e.g., generating a plot summary for a real movie not in the dataset).
- **the fallback:** the universal system prompt enforces a mandatory fallback. if a requested entity is missing from the rag context, the agent must immediately abort and return `{"error": "this information is not available in the current cinema policy dataset."}`. the orchestrator detects this specific error key and safely informs the user.

## 3. contextual deficits during routing
a user might trigger the "book ticket" intent without providing enough information to actually process the transaction.
- **the risk:** agent 3 (pricing) and agent 4 (demand) are triggered with null values for `movie_name` or `num_tickets`, causing calculation errors or meaningless demand predictions.
- **the fallback:** the orchestrator acts as a gatekeeper. before calling agents 3, 4, and 5, it checks the `st.session_state.booking_context`. if essential keys are missing, it halts the multi-agent cascade and prompts the user: "i can help with that. could you please provide the movie name, date, and number of tickets?"

## 4. security interventions and fraud triggers
adversarial inputs or malicious booking patterns represent a critical failure of the business logic.
- **the risk:** a user attempts to exploit a discount code or execute a denial-of-service via rapid ticket cancellations.
- **the fallback:** agent 5 evaluates the context of every booking intent. if the `risk_category` is flagged as "high", the orchestrator immediately intercepts the flow, overrides the pricing and demand outputs, and returns a hard block to the user: "security alert: transaction blocked."

## 5. api latency and downtime
the system relies entirely on external api calls to the groq platform.
- **the risk:** api rate limits, network timeouts, or groq server downtime.
- **the fallback:** while currently relying on streamlit's native spinner for ui feedback during latency, production implementations would wrap `call_llm` in a robust retry mechanism (like the `tenacity` library) with exponential backoff to handle transient network failures gracefully.