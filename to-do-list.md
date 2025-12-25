Phase 1: Project Initialization & Infrastructure
This phase sets up the foundation, ensuring your containers can talk to each other.

[x] Initialize Project Structure

Create the root directory CSV-Sorter_2.0.
Initialize a Git repository.
Create the following sub-directories: frontend/, migrations/, AI_Project_Root/.
[x] Define Dependencies

Create a requirements.txt for the Python environment.
Key packages: fastapi, uvicorn, psycopg2-binary, tensorflow, torch, scikit-learn, sentence-transformers, pgvector.
[ ] Docker Configuration (optional — deprecated if you choose Cloudflare-managed deployment)

Create a Dockerfile for the Python environment (shared by app and worker) — **optional**.
Create docker-compose.yml — **optional** and intended only for local development and testing.
If you choose Docker for local dev, define the db, app and worker services as before; otherwise skip Docker and proceed with Cloudflare-based deployment.

Cloudflare-based Infrastructure (recommended)

- Use **Cloudflare D1** for relational storage (products, feedback). Note: D1 is SQLite-compatible and does not support pgvector.
- Use **Cloudflare Pages** for the frontend and **Cloudflare Workers / Pages Functions** for the backend API.
- Use **Cloudflare R2** to store CSV backups, model artifacts, and any large binary blobs.
- Decide on **embedding strategy** (see options below).
- Configure Cloudflare environment bindings/secrets for D1, R2 and any managed embedding APIs.
- Update deployment scripts and CI to publish to Cloudflare Pages/Workers instead of docker-compose.
Phase 2: Database Layer
Setting up the storage for data and vector embeddings.

[x] Database Setup
[x] Database Connection

Configure **Cloudflare D1** to store the products and feedback metadata (D1 is SQLite-compatible).
Decide how to store and search embeddings (pgvector is not available in D1 — choose one of the embedding strategies below):
- **Option A (recommended)**: Use a managed embeddings API (OpenAI/Hugging Face) and a managed vector DB (Pinecone, Supabase Vector, etc.). Store metadata and pointers (vector IDs) in D1.
- **Option B**: Keep a dedicated ML worker (VM or cloud instance) to generate embeddings and store them in an external vector DB. D1 stores metadata and pointers.
- **Option C**: For small datasets only, store embeddings directly in D1 as JSON blobs and perform linear or app-level approximate search (works for prototypes only).
Create environment variables/secrets for D1, R2 (for backups), and any managed embedding/vector DB API keys. Update application code to use D1-compatible SQL/clients instead of psycopg2 where applicable.
[x] Schema Design (migrations/)

Create SQL scripts in the migrations/ folder.
Run the SQL scripts in migrations/ against the external database (manually or via a script).
Table 1: products (stores raw CSV data, ID, text content).
Table 2: embeddings — store vector metadata and either pointers to an external vector DB or (for small datasets) a JSON blob of the embedding vector in D1. Choose search/indexing strategy according to the embedding option selected.
Table 3: feedback (stores human approvals/corrections linked to product IDs).
Phase 3: Machine Learning Core (AI_Project_Root/)
Building the logic that powers the "Intelligence" of the system.

[x] Embedding Logic

Create AI_Project_Root/embedding_worker.py.
Implement logic to load sentence-transformers.
Write a function to read new products from the DB, generate embeddings, and save them to the embeddings table.
[x] Feedback Logic

Logic integrated into retrain_model.py to query the feedback table directly.
[x] Retraining Logic

Create AI_Project_Root/retrain_model.py (Postgres) and an SQLite-friendly retrain script `AI_Project_Root/retrain_model_sqlite.py` (lightweight, on-device).
- **Completed**: Implemented `AI_Project_Root/retrain_model_sqlite.py` that trains a small `TfidfVectorizer + LogisticRegression` classifier from feedback pairs and saves `normalization_model.joblib`.
- **Added**: `AI_Project_Root/Consolidate_feedback.py` to export feedback pairs to CSV for inspection or alternate training.
- **Next**: Optional: fine-tune a SentenceTransformer model for embeddings and similarity-based retrieval when you need semantic generalization.
- **Added**: `scripts/demo_retrain_and_reload.py` — seeds feedback, runs the SQLite retrain, and reloads the model for a quick local verification.
Phase 4: Backend Development (app)
Creating the API that connects the database, ML logic, and Frontend.

[x] FastAPI Setup

Create main.py.
Initialize the FastAPI app.
Set up the database connection using psycopg2.
[ ] API Endpoints

[x] GET /products-for-review: Query the DB for products with low confidence or no feedback. Return original data + model suggestion.
[x] POST /submit-feedback: Accept JSON payload (product ID, approved status, corrected text) and insert into the feedback table.
[x] POST /upload-csv: Endpoint to upload a CSV file and populate the products table.
[x] POST /trigger-retrain: Endpoint to manually trigger the retrain_model.py script.
POST /load-model: Endpoint to reload the normalization model into memory without restarting the server.
Phase 5: Frontend Development (frontend/)
Building the Human-in-the-Loop interface.

[x] React Setup

Inside frontend/, run npm create vite@latest . (select React).
Install Tailwind CSS and configure tailwind.config.js.
[x] UI Components

Create a Review Card component to display:
Original Data.
Model Suggestion.
"Approve" Button.
"Correct" Input Field + Submit Button.
[x] API Integration

Implement fetch or axios calls to GET /products-for-review on component mount.
Implement POST calls to /submit-feedback when the user interacts with the buttons.
Phase 6: Integration & Orchestration
Connecting the pieces.

[x] Worker Implementation

Ensure the worker service in Docker Compose runs a loop or a job queue (like Celery or a simple while loop) that executes embedding_worker.py when new data arrives.
[x] Data Ingestion

Create a simple script or endpoint to upload a CSV file and populate the products table to start the flow.
[ ] Final Testing

Final Testing

- Deploy the frontend to **Cloudflare Pages** and the backend to **Cloudflare Workers / Pages Functions** (or run locally for smoke tests).
- Provision **D1** and any external vector DB or managed embedding service.
- Ingest sample data and verify products appear in D1.
- Verify embeddings are generated and stored according to the chosen strategy (external vector DB, R2+FAISS on a worker/VM, or D1 JSON for small datasets).
- Open the frontend (Cloudflare Pages preview or live) and review an item.
- Verify feedback is saved in D1 and retrain workflow (if applicable) runs as expected.
Phase 7: Future Deployment (Optional)
Steps to take when you are ready to share the application with others.

[ ] Frontend & Backend Deployment (Cloudflare)

- **Frontend (Cloudflare Pages)**: Connect GitHub repo to Pages and configure build settings (Build command: npm run build, Output directory: dist).
- **Backend (Cloudflare Workers / Pages Functions)**: Convert/port FastAPI endpoints to a deployable serverless function (or use a lightweight HTTP server on a small VM if you need full Python runtime).
  - If you need Python runtime for the backend and cannot run it in Workers, consider Cloudflare Workers with a lightweight JS/Rust edge handler, or keep the backend on a small managed VM (or use Cloud Run / Fly / Railway) and front it with Cloudflare.
- **D1**: Create and bind a D1 database to your Worker/Pages deployment.
- **R2**: Configure R2 for CSV backups and model artifacts.
- Update the frontend config to point to the deployed backend URL and test end-to-end.


Decision required (short)

- **Choose embedding & retrain strategy**:
  - Option A (recommended): Use a managed embeddings API + managed vector DB; keep D1 for metadata.
  - Option B: Keep a dedicated ML worker on a VM and use FAISS/external vector DB; D1 stores metadata.
  - Option C (prototype only): Store embeddings as JSON in D1 and perform linear/approx search in app code.

The Workflow

Connection: The embedding_worker.py script should be updated to connect to D1 (or to an external vector DB) and/or to use a managed embeddings API.
Reading: Query D1 for unprocessed products.
Processing: Convert the product text into an embedding (via managed API or a worker) and store per the chosen strategy.
Writing: Save metadata to D1 and embeddings to the chosen vector storage (managed DB or R2/FAISS/JSON).