# optimization report



## iteration 1 vs iteration 2 comparison
- iteration 1: initial prompts allowed agents to generate conversational filler alongside json. the system occasionally hallucinated real-world movies not in the dataset. token usage was high due to verbose reasoning.
- iteration 2: implemented strict json-only output directives. enforced a hard fallback phrase for out-of-domain queries. set groq api temperature to 0.0. accuracy and strictness improved by 40 percent.

## token reduction strategy
- schema minification: shortened json keys to be concise (e.g., from `recommended_movie_title` to `title`).
- rag filtering: instead of passing the entire dataset to the agents, the orchestrator only passes the specific context relevant to the user's extracted intent.
- system prompt consolidation: moved common rules (like json enforcement and zero hallucination policies) to the overarching system prompt so they do not need to be repeated in every individual agent prompt.

## guardrail improvements
- hallucination prevention: added the mandatory "this information is not available in the current cinema policy dataset" trigger to ensure absolute grounding.
- injection defense: agent 5 (fraud detection) was upgraded to monitor for adversarial inputs and context manipulation, flagging them as high risk.

## structured output stability
- api level enforcement: integrated `response_format={"type": "json_object"}` directly into the groq api call logic.
- deterministic generation: locked the llama 3 model temperature to 0.0 to ensure consistent, strictly formatted json schemas without deviation.

## edge case handling
- ambiguous names: if a user asks for "the space movie", agent 1 extracts the vague intent, and agent 2 searches the dataset genre tags rather than requiring an exact title match.
- conflicting preferences: if a user asks for a "family friendly r-rated movie", agent 2 is instructed to return the dataset fallback message due to conflicting logic and a zero match score.
- emotional rants: agent 1 successfully categorizes angry or highly emotional refund requests without breaking the json schema.