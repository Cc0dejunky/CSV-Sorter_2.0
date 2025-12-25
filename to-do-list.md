Phase 1: Project Initialization & Infrastructure
This phase sets up the foundation, ensuring your containers can talk to each other.

[x] Initialize Project Structure

Create the root directory CSV-Sorter_2.0.
Initialize a Git repository.
Create the following sub-directories: frontend/, migrations/, AI_Project_Root/.
[x] Define Dependencies

Create a requirements.txt for the Python environment.
Key packages: fastapi, uvicorn, psycopg2-binary, tensorflow, torch, scikit-learn, sentence-transformers, pgvector.
[x] Docker Configuration

Create a Dockerfile for the Python environment (shared by app and worker).
Create docker-compose.yml.
Define the db service: Use a PostgreSQL image and configure the environment variables for user/password.
Define the app service: Maps to your FastAPI backend, exposing port 8000.
Define the worker service: Runs the background ML tasks.
Phase 2: Database Layer
Setting up the storage for data and vector embeddings.

[x] Database Setup
[x] Database Connection

Configure the PostgreSQL container to initialize with the pgvector extension enabled.
Obtain credentials for the external PostgreSQL database.
Create a .env file with POSTGRES_HOST, POSTGRES_USER, etc.
Ensure the external database has the pgvector extension enabled.
[x] Schema Design (migrations/)

Create SQL scripts in the migrations/ folder.
Run the SQL scripts in migrations/ against the external database (manually or via a script).
Table 1: products (stores raw CSV data, ID, text content).
Table 2: embeddings (stores vector representations using pgvector types).
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

Create AI_Project_Root/retrain_model.py.
Implement the training loop using tensorflow or torch (as per your preference) to fine-tune the model based on the consolidated feedback.
Implement logic to save the new model version to disk.
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

Run docker-compose up --build.
Ingest sample data.
Verify embeddings are generated in the DB.
Open localhost (Frontend), review an item.
Verify feedback is saved in DB.
Trigger retrain and verify the model file updates.
Phase 7: Future Deployment (Optional)
Steps to take when you are ready to share the application with others.

[ ] Frontend Deployment (Cloudflare Pages)

Connect GitHub repo to Cloudflare Pages.
Configure build settings (Build command: npm run build, Output directory: dist).
[ ] Backend Exposure (Cloudflare Tunnel)

Install cloudflared (Cloudflare Tunnel) on the host machine.
Create a tunnel to route traffic from a public domain (e.g., api.yourdomain.com) to localhost:8000.
Update frontend API URL to point to the new secure domain.


The Workflow
Connection: The embedding_worker.py script connects to the PostgreSQL service defined in your docker-compose.yml using the psycopg2 library.
Reading: It queries the products table to find items that haven't been processed yet (e.g., where processed = False or by checking for missing IDs in the embeddings table).
Processing: It uses sentence-transformers to convert the product text into a vector (a list of numbers).
Writing: It executes an SQL INSERT statement to save that vector into the embeddings table.