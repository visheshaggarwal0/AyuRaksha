# AyuRaksha — Free Production Deployment Guide (Render + Vercel + Neon)

This guide walks you through deploying the complete AyuRaksha platform with **zero hosting cost** and **no credit card required**.

---

## 🏗️ Architecture Overview

- **Frontend:** [Vercel](https://vercel.com) (React 18 + Vite SPA, Global Edge CDN, SSL, Custom Domain)
- **Backend:** [Render](https://render.com) (FastAPI, Uvicorn, CPU-optimized Sentence-Transformers)
- **Database:** [Neon](https://neon.tech) (Serverless PostgreSQL + PGVector HNSW index)

---

## 🚀 Step 1: Deploy Backend on Render (5 minutes)

1. Sign up or log into [Render.com](https://render.com) using your **GitHub account**.
2. Click **New +** → **Web Service**.
3. Select **Build and deploy from a Git repository** and pick your `AyuRaksha` repo.
4. Configure the Web Service settings:
   - **Name:** `ayuraksha-backend`
   - **Region:** `Singapore` (or closest to India)
   - **Branch:** `main`
   - **Root Directory:** *(leave blank)*
   - **Runtime:** `Python 3`
   - **Build Command:** `./render_build.sh`
   - **Start Command:** `uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port $PORT`
   - **Instance Type:** **Free** (512 MB RAM / 0.1 CPU)
5. Under **Environment Variables**, add:
   | Key | Value | Purpose |
   | :--- | :--- | :--- |
   | `PYTHON_VERSION` | `3.11.9` | Ensures Python 3.11 runtime |
   | `APP_ENV` | `production` | Production mode |
   | `DATABASE_URL` | `postgresql+asyncpg://...` | Your Neon Postgres connection string |
   | `ALLOWED_ORIGINS` | `https://ayuraksha.vercel.app` | Comma-separated allowed frontend URLs |
   | `BHASHINI_API_KEY` | *(Your ULCA API key)* | Optional for live Bhashini NMT |
   | `BHASHINI_USER_ID` | *(Your Bhashini User ID)* | Optional for live Bhashini NMT |
   | `BHASHINI_PIPELINE_ID` | *(Your Pipeline ID)* | Optional for live Bhashini NMT |
   | `GROQ_API_KEY` | *(Your Groq API key)* | Optional for Llama-3.3-70B synthesis |
   | `GEMINI_API_KEY` | *(Your Gemini API key)* | Optional for Gemini synthesis |
6. Click **Create Web Service**.
7. Once deployed, note down your Render URL:
   `https://ayuraksha-backend.onrender.com`

---

## 🌐 Step 2: Deploy Frontend on Vercel (3 minutes)

1. Sign up or log into [Vercel.com](https://vercel.com) with your **GitHub account**.
2. Click **Add New...** → **Project** and import your `AyuRaksha` repo.
3. In the project setup screen:
   - **Framework Preset:** `Vite`
   - **Root Directory:** Click Edit and select **`frontend`**
   - **Build Command:** `npm run build` *(default)*
   - **Output Directory:** `dist` *(default)*
4. Expand **Environment Variables** and add:
   - **Name:** `VITE_API_BASE_URL`
   - **Value:** `https://ayuraksha-backend.onrender.com` *(Replace with your actual Render URL from Step 1)*
5. Click **Deploy**.
6. In ~45 seconds, Vercel will assign your public URL (e.g. `https://ayuraksha.vercel.app`).

---

## ⏰ Step 3: Prevent Free-Tier Sleep During Hackathons (Keep-Warm)

Render's free tier spins down after 15 minutes of zero traffic. To ensure SIH evaluators get instant sub-second responses:

1. Sign up for free at [cron-job.org](https://cron-job.org) or [UptimeRobot.com](https://uptimerobot.com).
2. Create a new HTTP Monitor:
   - **URL:** `https://ayuraksha-backend.onrender.com/health`
   - **Interval:** Every **10 minutes**
3. This sends a lightweight `GET /health` request that keeps the FastAPI process warm and ready 24/7 during evaluation periods.

---

## 🧪 Step 4: Verification Checklist

- [ ] Open `https://ayuraksha-backend.onrender.com/health` → returns `{"status":"healthy","database_configured":true,"database_reachable":true}`
- [ ] Open `https://ayuraksha-backend.onrender.com/docs` → interactive Swagger API documentation loads cleanly.
- [ ] Open your Vercel frontend URL → Landing page loads with official AyuRaksha shield and logo.
- [ ] Submit a Section 3(p) query in the Copilot → Tokens stream in real time via Server-Sent Events (SSE).
- [ ] Click any citation badge → Verifiable Gazette chunk and SHA-256 cryptographic provenance modal displays.
