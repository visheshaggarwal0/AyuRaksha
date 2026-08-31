# AyuRaksha — Product & Engineering Documentation

**AyuRaksha: An AI IP & Regulatory Navigator for Ayurvedic Innovation**  
*Built for Smart India Hackathon (SIH 26045) — Ministry of Ayush & AIIA*

---

## 1. Core Tech Stack

* **Frontend:** React 18 + Vite + TypeScript + Tailwind CSS (Responsive regulatory workspace)
* **Backend:** Python 3.11+ + FastAPI + SQLAlchemy 2.0 (Async) + Pydantic v2
* **Relational & Vector Database:** Neon Serverless PostgreSQL + `pgvector` (`hidden-wind-77590258`)
* **Object Storage & Auth:** Firebase Cloud Storage (5 GB free for PDFs) + Firebase Auth
* **Decision Engines:** Deterministic Decision Trees (Drugs & Cosmetics Act 1st Schedule + BDA 2023) + Verified Citation Entailment

---

## 2. Quick Start for Team

### Backend (FastAPI + Neon Postgres)
```bash
# 1. Enter backend directory and install dependencies
cd backend
pip install -r requirements.txt

# 2. Configure .env with your Neon credentials
# (Copy from .env.example if needed)

# 3. Initialize database tables and pgvector extension
python -m app.db.init_db

# 4. Run the development server
uvicorn app.main:app --reload --port 8000
```
API Documentation will be live at `http://127.0.0.1:8000/docs`.

### Frontend (React + Vite + Tailwind)
```bash
# 1. Enter frontend directory and install dependencies
cd frontend
npm install

# 2. Run local development server
npm run dev
```
The web application will open at `http://localhost:5173`.

---

## 3. Documentation Index

1. [`Documentation/01_PRD.md`](file:///c:/Users/aggar/Documents/AyuRaksha/Documentation/01_PRD.md) — Product Requirements Document
2. [`Documentation/02_TRD.md`](file:///c:/Users/aggar/Documents/AyuRaksha/Documentation/02_TRD.md) — Technical Requirements Document
3. [`Documentation/03_App_Flow.md`](file:///c:/Users/aggar/Documents/AyuRaksha/Documentation/03_App_Flow.md) — Screen map and user journeys
4. [`Documentation/04_UIUX_Brief.md`](file:///c:/Users/aggar/Documents/AyuRaksha/Documentation/04_UIUX_Brief.md) — Visual and interaction design tokens
5. [`Documentation/05_Backend_Schema.md`](file:///c:/Users/aggar/Documents/AyuRaksha/Documentation/05_Backend_Schema.md) — Database and security model
6. [`Documentation/06_Implementation_Plan.md`](file:///c:/Users/aggar/Documents/AyuRaksha/Documentation/06_Implementation_Plan.md) — Build roadmap & SIH evaluation metrics
