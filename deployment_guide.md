# Leagle AI: Deployment Guide (Free Tier Strategy)

This guide outlines how to launch Leagle AI into production using industry-standard free hosting platforms.

---

## 1. Frontend: Next.js (Vercel)
**Platform**: [Vercel](https://vercel.com)
Vercel is the natural choice for Next.js. It offers a generous free tier with automatic CI/CD from GitHub.

### Steps:
1.  Push your `frontend/` directory to a GitHub repository.
2.  Import the project into Vercel.
3.  Set the **Root Directory** to `frontend`.
4.  Configure **Environment Variables**:
    *   `NEXT_PUBLIC_API_URL`: The URL of your backend (from Step 2). **IMPORTANT**: Must include `https://` prefix (e.g., `https://leagle-backend.hf.space`).
    *   `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`: From your Clerk Dashboard.
    *   `CLERK_SECRET_KEY`: From your Clerk Dashboard.

---

## 2. Backend Options (Free Tier)

### Option A: Render
**Platform**: [Render](https://render.com)
Good for simple Python deployments.

*   **Build Command**: `pip install -r requirements.txt`
*   **Start Command**: `python -m uvicorn main:app --host 0.0.0.0 --port 10000`

### Option B: Hugging Face Spaces (Recommended for Performance)
**Platform**: [Hugging Face](https://huggingface.co/new-space)
Excellent for AI backends. It offers better performance and persistent URLs.

1.  Create a **New Space**.
2.  Select **Docker** as the Space SDK.
3.  Upload the `backend/` directory content (including the new `Dockerfile`).
4.  HF will automatically build and expose the API on port 7860.
5.  **Important**: In the Space **Settings**, add your secrets:
    *   `ALLOWED_ORIGINS`: Your Vercel frontend URL (e.g., `https://your-app.vercel.app`).
    *   `DATABASE_URL`, `GEMINI_API_KEY`, etc.

---

## 3. Database: PostgreSQL (Neon)
**Platform**: [Neon.tech](https://neon.tech)
Neon provides a serverless PostgreSQL database with a robust free tier.

### Steps:
1.  Create a project on Neon.
2.  Copy the **Connection String**.
3.  Ensure your backend uses this string as `DATABASE_URL`.
4.  Leagle is already configured to auto-create tables on startup, so no migration scripts are needed for the first launch.

---

## 4. Vector Store: Qdrant (Cloud)
**Platform**: [Qdrant Cloud](https://cloud.qdrant.io)
You are already connected to a Qdrant cluster in the current dev environment.

### Steps:
1.  Use your existing `QDRANT_URL` and `QDRANT_API_KEY`.
2.  Ensure the `regulations_v1` collection is persistent.

### GitHub Actions Keep-Alive
If your Hugging Face Space or Qdrant cluster is on a free or idle-sensitive tier, add these repository secrets and keep the scheduled workflow enabled:

* `HF_BACKEND_URL` - your Hugging Face backend URL, for example `https://your-space.hf.space`
* `QDRANT_URL` - your Qdrant Cloud base URL
* `QDRANT_API_KEY` - your Qdrant API key, if the cluster requires one

The workflow runs every 10 minutes and calls the backend `/health` endpoint plus Qdrant `/readyz` so both services stay warm.

---

## Summary of URL Configuration
To make the frontend and backend talk to each other in production:
1.  Deploy the **Backend** first to get its public URL (e.g., `https://leagle-backend.onrender.com`).
2.  Add that URL to the Frontend's `NEXT_PUBLIC_API_URL` variable.
3.  Redeploy the Frontend.

### Troubleshooting HF + Vercel
1.  **CORS Errors**: Ensure `ALLOWED_ORIGINS` in HF Spaces includes your Vercel URL.
2.  **Mixed Content**: Ensure `NEXT_PUBLIC_API_URL` starts with `https://`.
3.  **Port 7860**: HF Spaces expects port 7860. The `Dockerfile` is pre-configured for this.
4.  **Trailing Slashes**: Some routers are sensitive to trailing slashes. Use `/api/regulations` instead of `/api/regulations/` if you hit 404s.

### Deployment Cost: $0.00
This entire stack can run on free tiers for the initial hackathon/demo phase.
