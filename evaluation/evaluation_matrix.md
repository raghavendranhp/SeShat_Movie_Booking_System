# Evaluation Matrix & Performance Analysis

Based on the automated batch testing of 30 edge-case scenarios, the multi-agent system's performance is broken down below:

### 1. The Matrix

| Metric | Score / Result | Methodology & Observations |
| --- | --- | --- |
| **Intent Accuracy** | **77% (23/30)** | Agent 1 correctly classified the vast majority of intents. Notably, 2 of the 7 "failures" (ts_017, ts_020) were actually successful re-routings: the user asked to book 80-100 tickets, and the agent smartly routed them to `bulk/corporate booking` rather than standard booking. |
| **Recommendation Accuracy** | **Pass / High** | Handled ambiguous queries ("little paws") and conflicting preferences (ts_021-024) by strictly adhering to the RAG dataset constraints. |
| **Pricing Logic Correctness** | **Pass / High** | When evaluated in the Streamlit UI, Agent 3 correctly calculated base prices and stacked multipliers (e.g., weekend + occupancy surge). |
| **Fraud Detection Quality** | **Pass / High** | Simulated fraud attacks (rapid cancellations, cross-account discount abuse) successfully triggered high-risk scores from Agent 5 during booking flows. |
| **Hallucination Rate** | **0%** | The system exhibited zero hallucinations. Queries for out-of-dataset movies ("Spider-Man") and directors ("Christopher Nolan") successfully hit the fallback guardrail. |
| **JSON Consistency** | **100%** | Across 30 automated API calls, the Llama-3-8b model (temperature = 0.0) never broke the JSON schema, resulting in zero parsing crashes. |
| **Token Efficiency** | **Highly Optimized** | Dynamic RAG injection proved highly efficient. Simple intents consumed ~940 tokens. Recommendations consumed ~2,600 tokens (loading only `movies.json`). Full bookings consumed ~4,200 tokens (loading pricing + sales datasets simultaneously). |

### 2. Deep Dive: Token Consumption Analysis

The script generated excellent data on how dynamic routing saves API costs. Because the orchestrator only injects the datasets required for the specific intent, we see a clear three-tier token consumption pattern:

* **Tier 1: Basic Routing (~940 tokens):** Queries like checking refund status, canceling tickets, or bulk booking only require Agent 1. No heavy datasets are loaded.
* **Tier 2: Recommendations (~2,550 - 2,650 tokens):** Requires Agent 1 + Agent 2, plus the injection of the `movies.json` dataset.
* **Tier 3: Complex Transactions (~4,150 - 4,260 tokens):** Standard ticket booking requires the most processing power. It triggers Agent 1, then simultaneously triggers Agent 3 (Pricing), Agent 4 (Demand), and Agent 5 (Fraud), injecting both `pricing_rules.json` and `historical_sales.json`.

