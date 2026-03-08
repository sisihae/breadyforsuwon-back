# Project Overview

Bready for Suwon is an agent-orchestrated local discovery system for bakeries in Suwon, South Korea.

The goal of this project is to experiment with production-oriented LLM agent architectures, rather than building a simple chatbot or RAG application.

The system follows the principle:
Human defines goals and policies → agents execute workflows.

---

# Core System Architecture

The system follows this agent workflow:

Human (Goal / Policy)
→ Planner Agent
→ Execution Agents
→ QA / Policy Agent
→ Evaluation System
→ Logging / Rollback

Important rule:

This repository must not evolve into a single monolithic LLM pipeline. Each stage of the workflow should remain clearly separated.

---

# Design Philosophy

This project focuses on Applied AI system design.

Engineering goals:

1. Problem decomposition
2. Agent orchestration
3. Tool integration
4. Eval-driven development
5. Production-minded architecture

Claude should prefer designs that support these goals.

---

# Agent Architecture

## 1. Planner Agent

Responsibilities

- Parse the user query
- Identify user intent
- Generate a structured execution plan

Example output:

```json
{
  "intent": "bakery_recommendation",
  "filters": {
    "product": "croissant",
    "location": "Suwon"
  },
  "tasks": ["retrieve_reviews", "filter_bakeries", "rank_candidates"]
}
```

The planner must not call tools directly.

---

## 2. Execution Agents

Execution agents perform tool-based tasks.

### 2-1. Retrieval Agent

Responsibilities

- Search bakery reviews using vector embeddings
- Return relevant bakery candidates

Tools

- Weaviate vector search
- embedding similarity

### 2-2. Tag Filter Agent

Responsibilities

- Filter bakeries by structured attributes

Tools

- PostgreSQL queries

### 2-3. Map Agent

Responsibilities

- Fetch bakery location data
- Integrate Kakao Map API

---

## 3. Context Aggregation

Combine results from execution agents into a single context object.

Example structure:

```json
{
  "candidate_bakeries": [],
  "review_snippets": [],
  "metadata": {}
}
```

---

## 4. Response Generator

Uses the aggregated context to generate recommendations.

Responsibilities

- Explain recommendations
- Avoid hallucinating bakeries
- Reference retrieved context

---

## 5. QA / Policy Agent

The QA agent validates outputs before returning them to the user.

Checks include

- hallucination detection
- policy compliance
- database existence verification

Example validation rules

- recommended bakery exists in database
- bakery is located in Suwon
- response references retrieved context

---

## 6-1. Evaluation System

LLM outputs are non-deterministic, so evaluation must be metric-based.

Example metrics

- retrieval relevance score
- hallucination rate
- policy violation rate

Evaluation should be implemented as a separate module, not mixed with generation logic.

---

## 6-2. Fallback Strategy

If the QA agent fails validation:
Fallback to deterministic search.

Example fallback methods

- SQL tag filtering
- rule-based bakery ranking

---

## 7. Logging System

Each request should produce an agent trace.

Example log structure:

```json
{
  "user_query": "...",
  "planner_output": "...",
  "tools_called": [],
  "retrieved_data": [],
  "generated_response": "...",
  "qa_result": "...",
  "model_version": "..."
}
```

Logs should allow debugging of agent behavior.

---

# Target Repository Structure

The project should gradually move toward this structure:

```
agents/
planner_agent.py
retrieval_agent.py
tag_filter_agent.py
qa_agent.py

core/
workflow.py
agent_runner.py

tools/
vector_search.py
db_queries.py
map_api.py

evals/
retrieval_eval.py
hallucination_eval.py

logging/
trace_logger.py
```

Claude should prefer adding code that follows this architecture.

---

# Development Guidelines

When generating code:

1. Prefer modular agent design
2. Keep tool logic separate from agent logic
3. Avoid tightly coupling LLM prompts with infrastructure
4. Keep evaluation logic separate from generation
5. Write simple and readable Python modules
