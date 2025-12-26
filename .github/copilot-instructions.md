# Copilot Instructions — CSV-Sorter_2.0

Summary
- Small, single-repo full-stack app for cleaning/normalizing product text via an ML loop (human-in-the-loop).
- Key pieces: FastAPI backend (`main.py`), ML worker (`AI_Project_Root/embedding_worker.py`), retraining script (`AI_Project_Root/retrain_model.py`), and a minimal React UI (`App.jsx`).

Quick architecture notes (what to know first)
- There are two runtime roles: `app` (FastAPI HTTP server) and `worker` (embedding generator). Both are built from the same Dockerfile and orchestrated by `docker-compose.yml`.
- The system assumes an external PostgreSQL database with the `pgvector` extension — embeddings are stored in an `embeddings` table and used for similarity queries.
- Human feedback (approved/corrected text) is stored in `feedback` and used to fine-tune the SentenceTransformer model.

Files & patterns to reference
- `main.py` — all API endpoints and DB access patterns; look here for how the frontend talks to the API and how suggestions/confidence are computed.
  - Endpoints: `GET /products-for-review`, `POST /submit-feedback`, `POST /upload-csv`, `POST /trigger-retrain`.
  - Confidence is computed by: nearest approved product using `pgvector` operator `<=>` and then `confidence = max(0, 1 - distance)` (see `get_products_for_review`).
- `AI_Project_Root/embedding_worker.py` — looks for products without embeddings (LEFT JOIN where `e.product_id IS NULL`), encodes with `SentenceTransformer('all-MiniLM-L6-v2')` (384-dim), and inserts lists via `psycopg2`.
- `AI_Project_Root/retrain_model.py` — collects correction pairs (`original`, `correction`) and fine-tunes using `MultipleNegativesRankingLoss`. It requires at least **5** correction pairs to proceed.
- `App.jsx` — minimal example of the UI and payloads used to `submit-feedback` (JSON shape: `{product_id, is_approved, correction}`).
- `README.md` and `to-do-list.md` — contain useful developer context and the intended DB schema; note `migrations/` is referenced but not present in the repo.

Environment & runtime
- Required env vars (export or .env):
  - POSTGRES_HOST, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, (optional) POSTGRES_PORT
  - Optional Cloudflare R2 backup: R2_BUCKET_NAME, R2_ENDPOINT_URL, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY
- Note: `docker-compose.yml` expects an external Postgres by default (no `db` service present). The FastAPI DB defaults in code assume `DB_HOST='db'` for Docker setups but will use env vars when provided.

How to run locally (explicit commands)
- Start full stack (app + worker):
  - docker-compose up --build
- Start frontend (if you have a local frontend):
  - cd frontend && npm run dev
- Manually run worker or retrain for debugging:
  - python AI_Project_Root/embedding_worker.py
  - python AI_Project_Root/retrain_model.py

Concrete testing examples
- Upload CSV (multipart):
  - curl -X POST "http://localhost:8000/upload-csv" -F "file=@'sample_products - products_export.csv'"
- Get items for review:
  - curl http://localhost:8000/products-for-review
- Submit feedback (approve):
  - curl -X POST -H 'Content-Type: application/json' -d '{"product_id":1,"is_approved":true}' http://localhost:8000/submit-feedback
- Submit feedback (correction):
  - curl -X POST -H 'Content-Type: application/json' -d '{"product_id":1,"is_approved":false,"correction":"Correct name"}' http://localhost:8000/submit-feedback
- Trigger retrain (starts background task when called from API):
  - curl -X POST http://localhost:8000/trigger-retrain

Important conventions & caveats
- Model: `all-MiniLM-L6-v2` (SentenceTransformers). Retraining is shallow by default (1 epoch) and saved to `./fine_tuned_model` (then optionally backed up to R2).
- The worker and retrain scripts write/read directly to the DB using simple SQL via `psycopg2`; follow those SQL patterns when adding new queries.
- CORS is currently permissive (`allow_origins=['*']`) — lock this down in production.
- There are no automated tests in the repo; rely on local end-to-end testing with `docker-compose` for now.

Where to update this file
- If you add tests, a real `migrations/` folder, or a CI workflow, update this file with the relevant commands and files (migration names, test commands, CI job names).

If anything above is unclear or you want more examples (DB schema SQL, sample payloads, or typical debug steps) tell me which area to expand and I’ll iterate. ✅
