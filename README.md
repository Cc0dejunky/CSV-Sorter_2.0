# CSV-Sorter_2.0
# CSV-Sorter Application Analysis

This document provides a summary of the CSV-Sorter application, a full-stack system designed to clean and normalize product data using a machine learning pipeline with a human-in-the-loop feedback mechanism.

## Project Overview

The application is designed to process product data, likely from CSV files or other sources, and standardize it using machine learning models. It features a web interface for human reviewers to approve or correct the model's suggestions, and this feedback is used to retrain and improve the models continuously. The entire system is containerized using Docker for portability and ease of deployment.

## Architecture

The application is composed of three main services orchestrated by Docker Compose:

1.  **Backend (`app`)**: A Python backend built with **FastAPI**. It serves a REST API for the frontend, manages data ingestion, interacts with the database, and triggers background tasks.
2.  **Database**: An external **PostgreSQL** database (SaaS/Cloud) that stores product data and vector embeddings. **Note:** The database must support the `pgvector` extension.
3.  **ML Worker (`worker`)**: A dedicated background worker that performs computationally intensive machine learning tasks.

## Technologies

-   **Backend**: Python, FastAPI, `psycopg2` (for Postgres), `torch`, `scikit-learn`, `sentence-transformers`.
-   **Frontend**: React, Vite, Tailwind CSS.
-   **Database**: PostgreSQL, `pgvector`.
-   **Infrastructure**: Docker (Runtime), Cloudflare (Edge/Security).

## Prerequisites

To develop and run this application, ensure you have the following installed:

-   **Docker & Docker Compose**: Essential for running the full stack.
-   **Python 3.10+**: Required if running backend scripts locally.
-   **Node.js & npm**: Required for setting up and running the React frontend.
-   **Cloudflare Account (Optional)**: For deploying the frontend via Cloudflare Pages and securing the backend via Cloudflare Tunnel.

## Core Components

-   `main.py`: The entry point for the FastAPI backend. It defines all API endpoints for:
    -   Fetching products for review (`get_products_for_review`).
    -   Submitting human feedback (`submit_feedback`).
    -   Uploading raw CSV data (`upload_csv`).
    -   Triggering model retraining (`trigger_retrain`).
    -   Loading the normalization models (`load_normalization_model`).

-   `docker-compose.yml`: Defines the multi-service architecture of the application, including the `app`, `db`, and `worker` services, their configurations, and how they are networked.

-   `AI_Project_Root/`: This directory contains the core logic for the machine learning pipeline:
    -   `embedding_worker.py`: A background worker that generates vector embeddings for product data.
    -   `retrain_model.py`: A script to retrain the normalization models based on human feedback.

-   `frontend/`: The source code for the React-based frontend application. It provides the user interface for reviewing and correcting product data.

-   `migrations/`: Contains SQL scripts for setting up and evolving the database schema. These scripts define the tables, indexes, and other database objects required by the application.

## Data Flow

1.  **Ingestion**: Product data is ingested into the system, likely through a webhook or a bulk upload, and stored in the PostgreSQL database.
2.  **Processing**: The `embedding_worker` processes the new data, generating vector embeddings that are stored in the database.
3.  **Review**: The React frontend fetches products for review from the FastAPI backend. The backend provides the original data, the model's suggestion, and other relevant information.
4.  **Feedback**: A human reviewer uses the frontend to approve the suggestion or provide a correction. This feedback is submitted to the backend via the `submit_feedback` endpoint and stored in the database.
5.  **Retraining**: Periodically, the `trigger_retrain` endpoint is called, which initiates a background task. The `retrain_model.py` script uses the collected feedback to retrain and improve the normalization models.

## Running Locally (Single User Mode)

Since this application is currently for personal use, the recommended way to run it is locally on your machine.

### 1. Configuration
Create a `.env` file in the root directory with your external database credentials:
```
POSTGRES_HOST=your-host
POSTGRES_USER=your-user
POSTGRES_PASSWORD=your-password
POSTGRES_DB=your-db
```

### 2. Backend & Worker
Run the following command to start the backend and AI worker:
```bash
docker-compose up --build
```
The API will be available at `http://localhost:8000`.

### 3. Frontend
Open a new terminal, navigate to the frontend folder, and start the development server:
```bash
cd frontend
npm run dev
```
Access the UI at `http://localhost:5173`.
