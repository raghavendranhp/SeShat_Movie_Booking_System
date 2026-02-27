# prompt architecture document

## overview
the seshat ai movie booking system employs a modular, role-based multi-agent prompt architecture. instead of relying on a single monolithic prompt, the system dynamically constructs prompts by combining a universal system guardrail, a role-specific agent instruction, and injected contextual data.

## architectural components

### 1. the universal system prompt
this is the foundational layer applied to every single api call. it enforces the non-negotiable rules of the system:
- strict json output requirements.
- the zero-hallucination policy.
- the mandatory fallback phrase for out-of-domain queries.
- objective, non-conversational execution.

### 2. the role-specific agent prompts
there are five distinct agent prompts, each designed with a narrow scope and a strict json schema:
- agent 1 (intent): focuses entirely on nlp classification and entity extraction.
- agent 2 (recommendation): focuses on matching user preferences against the injected movie dataset.
- agent 3 (pricing): focuses on logical deduction and arithmetic based on injected pricing rules.
- agent 4 (demand): focuses on pattern recognition against injected historical sales data.
- agent 5 (fraud): focuses on behavioral analysis and anomaly detection against booking patterns.

### 3. dynamic context injection (rag simulation)
to ground the agents in reality and prevent hallucination, the orchestrator injects strict json datasets directly into the prompt payload at runtime. 
- agent 2 only sees `movies.json`.
- agent 3 only sees `pricing_rules.json` and the user's current booking context.
- agent 4 only sees `historical_sales.json`.
this ensures token efficiency by not sending the entire database to every agent.

## execution flow
when a user submits a query, the prompt is constructed as follows:
`final_payload = [system_prompt] + [agent_x_prompt] + [injected_json_dataset] + [user_input]`

this precise compartmentalization ensures that the llama 3 8b model remains highly focused, predictable, and strictly bound to the provided cinema policy rulebook.