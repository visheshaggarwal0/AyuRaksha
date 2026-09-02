# ADR-002: Pluggable LLM Generation Gateway (Gemini, Groq, Local Models)

## Status
Accepted

## Context
AyuRaksha was previously coupled to hardcoded local Ollama or OpenRouter endpoints. If Ollama was offline or an API key was missing, the application would fail or trigger ungrounded fallbacks. Furthermore, hackathons and enterprise deployments require switching between commercial cloud APIs (Google Gemini, Groq) and fully offline air-gapped models (Ollama with Llama 3 / Mistral) without modifying application code.

## Decision
We establish a **Pluggable LLM Generation Gateway** under `backend/app/modules/generation/`.
The generation module defines an `ILLMProvider` interface and coordinates a prioritized hierarchy of adapters:
1. **Google Gemini Provider**: Native REST implementation using `gemini-1.5-flash` or `gemini-2.0-flash`.
2. **Groq Provider**: High-speed inference using `llama-3.3-70b-versatile` or `mixtral-8x7b-32768`.
3. **Local Ollama Provider**: Offline inference on `localhost:11434` (`llama3.1:8b`).
4. **OpenRouter Provider**: Multi-model fallback gateway.
5. **Deterministic Statutory Synthesizer**: Zero-dependency rule-based legal summarizer that formats provided statutory chunks without crashing if all external networks are unavailable.

## Rationale
- Decouples legal prompt engineering from provider-specific payload schemas.
- Supports offline air-gapped demonstrations (SIH venues with poor internet).
- Allows dynamic model switching via standard environment variables (`LLM_PROVIDER=gemini` or `LLM_PROVIDER=groq`).

## Consequences
- All providers must support system instructions, temperature controls, and structured JSON output mode where available.
