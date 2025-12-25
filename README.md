# CSV-Sorter
1. Backend Server (main.py)
Technology: FastAPI.

Purpose: The central "brain" that runs as a persistent service.

Key Responsibilities:

API Endpoints: Exposes endpoints like /get_products_for_review and /submit_feedback for client communication.

Data Ingestion: Handles Shopify webhooks (/shopify_webhook) or bulk CSV uploads (/bulk_stage_data).

ML Prediction: Uses a joblib model for initial attribute normalization on new data.

Database Interaction: Connects to PostgreSQL to store product data and user feedback.

2. Frontend Client (review_tui.py)
Technology: Python with requests and rich libraries.

Purpose: A Text-based User Interface (TUI) that acts as the "human" in the human-in-the-loop system.

Key Responsibilities:

User Interaction: Provides a menu-driven interface for the user.

Data Review: Fetches products flagged for review and displays them in a tabular format.

Submitting Corrections: Allows users to provide correct values and sends them to the server's API.

Server Management: Includes functions to start and stop the backend process.

3. Supporting Components
Database (PostgreSQL): The source of truth containing a products table for data and a training_feedback table to log corrections.

Offline Scripts: Includes Consolidate_feedback.py and Retrain_model.py to process feedback and generate improved models.

The Four-Step Feedback Loop
This cycle ensures the system continuously learns from human corrections.

Step 1: Predict
Data Arrives: Raw data enters via Shopify webhook or CSV.

Model Predicts: The normalize_color function uses the current normalization_model.joblib to predict a standard value (e.g., "Nvy" → "Navy").

Flag for Review: The server saves the prediction to the database and sets needs_review = TRUE.

Step 2: Review
User Starts TUI: The operator runs the review_tui.py script.

Fetch Queue: The user selects "Review Products," prompting the TUI to call the /get_products_for_review endpoint.

Display Data: The server returns all products where needs_review = TRUE for the user to see.

Step 3: Correct
User Provides Input: The user identifies incorrect predictions and enters the correct value.

Submit Feedback: The TUI sends the product_id, raw_value, and human_correction to the /submit_feedback endpoint.

Server Records Feedback: The server logs the correction in training_feedback and sets the product's needs_review status to FALSE.

Step 4: Retrain
Consolidate: Run `python AI_Project_Root/Consolidate_feedback.py --out feedback_pairs.csv` to export correction pairs for inspection.

Retrain: Run the lightweight on-device retrain `python AI_Project_Root/retrain_model_sqlite.py` (or call `POST /trigger-retrain`) to create a new `normalization_model.joblib` from feedback.

Deploy: The user selects "Reload Model" in the TUI, which calls `/reload_model` to load the new model into memory.
# CSV-Sorter Application Analysis

This document provides a summary of the CSV-Sorter application, a full-stack system designed to clean and normalize product data using a machine learning pipeline with a human-in-the-loop feedback mechanism.

## Project Overview

The application is designed to process product data, likely from CSV files or other sources, and standardize it using machine learning models. It features a web interface for human reviewers to approve or correct the model's suggestions, and this feedback is used to retrain and improve the models continuously. The entire system is containerized using Docker for portability and ease of deployment.

## Core Components

-   `main.py`: The entry point for the FastAPI backend. It defines all API endpoints for:
    -   Fetching products for review (`get_products_for_review`).
    -   Submitting human feedback (`submit_feedback`).
    -   Uploading raw CSV data (`upload_csv`).
    -   Triggering model retraining (`trigger_retrain`).
    -   Loading the normalization models (`load_normalization_model`).

-   `AI_Project_Root/`: This directory contains the core logic for the machine learning pipeline:
    -   `embedding_worker.py`: A background worker that generates vector embeddings for product data.
    -   `retrain_model.py`: A script to retrain the normalization models based on human feedback.

-   `frontend/`: The source code for the React-based frontend application. It provides the user interface for reviewing and correcting product data.

-   `migrations/`: Contains SQL scripts for setting up and evolving the database schema. These scripts define the tables, indexes, and other database objects required by the application.

## Running Locally (Single User Mode)

Since this application is currently for personal use, the recommended way to run it is locally on your machine.

1. Create a virtualenv and install dependencies:
```bash
python -m venv .venv
# Linux / WSL
source .venv/bin/activate
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -r requirements.txt
```
2. Apply migrations (this will create `dev.db` locally):
```bash
python scripts/run_migrations.py
```
3. (Optional) Insert sample products for testing:
```bash
python scripts/insert_sample_products.py
```
4. Start the backend server:
```bash
uvicorn main:app --reload --port 8000
```
5. Start worker (manually for now):
```bash
python AI_Project_Root/embedding_worker.py
```
6. Start frontend (if you have it locally):
```bash
cd frontend
npm install
npm run dev
```

### Local API endpoints (important for HITL flow)
- `POST /upload-csv` — upload products CSV; server will run the offline normalization model (if `normalization_model.joblib` exists) and insert rows into `products` with `needs_review` set accordingly.
- `GET /products-for-review` or `GET /get_products_for_review` — fetch items where `needs_review = true` for human review.
- `POST /submit-feedback` — submit correction payload: `{ "product_id": 123, "is_approved": true, "correction": "Correct Value" }`.
- `POST /trigger-retrain` — trigger retrain background job (keeps the offline retrain workflow).
- `POST /reload_model` — reload the `normalization_model.joblib` at runtime.

Review TUI (terminal)

You can run a terminal-based review interface that uses `rich` for display and `requests` to communicate with the API. It lets you list items needing review, approve items, submit corrections, reload the model, and trigger retraining.

Usage:

```bash
python review_tui.py --api http://localhost:8000
```

Controls:
- `l` / `list`: fetch and display products that need review
- choose a product by ID and then `a` to approve or `c` to correct
- `r` / `reload`: reload normalization model
- `t` / `trigger`: trigger retrain
- `q` / `quit`: exit the TUI

For full offline HITL testing on Windows, using WSL is recommended for better compatibility with ML tooling (FAISS / PyTorch).

