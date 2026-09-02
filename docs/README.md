# AyuRaksha — Documentation Hub

Welcome to the **AyuRaksha (आयुसुरक्षा)** documentation repository. This directory contains the complete canonical specifications, architectures, interaction designs, database schemas, and statutory regulatory guides developed for **Smart India Hackathon (SIH 26045)**.

---

## 📚 Master Documentation Index

All core documentation is organized into **6 comprehensive documents** directly in this directory:

| Document | Title | Description |
| :--- | :--- | :--- |
| **[`01_PRD.md`](./01_PRD.md)** | Product Requirements Document | Product vision, target personas, problem statement, core capabilities, and success metrics. |
| **[`02_TRD.md`](./02_TRD.md)** | Technical Requirements Document | Architecture principles, technology stack, dataflow pipeline, latency optimizations (~500ms TTFT), and security models. |
| **[`03_APP_FLOW.md`](./03_APP_FLOW.md)** | App Flow & User Journeys | Screen map, information architecture, and the 5 core user journeys (Inquiry, Graph, Classification, ABS, Dossier). |
| **[`04_UIUX_SPEC.md`](./04_UIUX_SPEC.md)** | UI/UX Design System & Tokens | Editorial design ethos, color tokens, typography, Framer Motion spring physics, and custom component specifications. |
| **[`05_ARCHITECTURE_AND_SCHEMA.md`](./05_ARCHITECTURE_AND_SCHEMA.md)** | System Architecture & Database Schema | Modular monolith diagram, Neon Serverless PostgreSQL + `pgvector` tables, Knowledge Graph engine, and key ADR summaries. |
| **[`06_REGULATORY_AND_INNOVATION_GUIDE.md`](./06_REGULATORY_AND_INNOVATION_GUIDE.md)** | Regulatory Frameworks & Innovation Guide | Detailed analysis of Patents Act 1970/2024, DCA 1940, BDA 2023, FSSAI 2022, 37 official Patent Forms, and SIH 26045 scorecard. |

---

## 🚀 Quick Reference

- **Backend Dev Server**: `uvicorn app.main:app --reload --port 8000` (API docs at `http://localhost:8000/docs`)
- **Frontend Dev Server**: `npm run dev` (Workspace at `http://localhost:5173`)
- **Primary LLM**: Google Gemini 2.5 Flash via Google AI Studio (`GEMINI_API_KEY`) with OpenRouter failover
- **Vector DB**: Neon Serverless PostgreSQL with `pgvector` HNSW index
