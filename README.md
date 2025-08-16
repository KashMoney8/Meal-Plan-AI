# RAG Meal Planner — Vertex AI Edition (Flask + LangChain + Pinecone + React + Postgres + Docker)

This build uses **Google Cloud Vertex AI** for both **generation (Gemini)** and **embeddings**.
No GPU VM needed. Pinecone remains the vector DB.

## Quick Start (Local Dev)
1) Put your Vertex **Service Account key** at `./secrets/gcp-sa.json` (do not commit).
2) Copy `.env.example` to `.env` and fill the Vertex and Pinecone values.
3) Place your recipes CSV at `data/recipes.csv`. (Use your uploaded dataset.)
4) Start:
   ```bash
   docker compose up --build
   ```
5) Ingest:
   ```bash
   docker compose exec backend python -m backend.ingestion.ingest_recipes --csv /app/data/recipes.csv
   ```
6) Open the app: http://localhost:5173

## Notes
- Models: `VERTEX_MODEL=gemini-1.5-pro`, `VERTEX_EMBED_MODEL=text-embedding-004` (configurable).
- Auth: `GOOGLE_APPLICATION_CREDENTIALS=/secrets/gcp-sa.json` in `.env`.
- Pinecone: set API key/index/namespace to match your account.
