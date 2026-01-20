# Medical Data Warehouse: Telegram-to-Analytical-API

This project automates the extraction of medical data from Telegram channels, transforms it into a structured Star Schema using dbt, enriches it with YOLOv8 nano object detection, and serves it via a FastAPI REST interface.

## 1. Prerequisites

* **Python 3.9+**
* **PostgreSQL** installed and running.
* **Telegram API Credentials** (API ID and Hash from [my.telegram.org](https://my.telegram.org)).

---

## 2. Environment Setup

### Create a Virtual Environment

First, clone the repository and set up a clean environment to manage dependencies.

```bash
# Create the environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

```

### Install Dependencies

Install all required libraries for scraping, database interaction, dbt, and the API.

```bash
pip install -r requirements.txt

```

### Environment Variables

Create a `.env` file in the root directory to store sensitive credentials:

```env
APP_API_ID=your_api_id
APP_API_HASH=your_api_hash
DB_USER=your_postgres_user
DB_PASSWORD=your_postgres_password
DB_NAME=medical_warehouse

```

---

## 3. Database & dbt Configuration

1. **Initialize dbt**: Ensure your `profiles.yml` is configured to point to your local PostgreSQL instance.
2. **Verify dbt Connection**:
```bash
cd medical_warehouse
dbt debug

```


3. **Run Initial Seed**: Upload the YOLO detection CSVs to the database.
```bash
dbt seed

```



---

## 4. Running the Components Manually

### Step A: The API (Data Access)

To start the REST API and view the documentation:

```bash
uvicorn api.main:app --reload

```

* **Access UI**: Visit `http://127.0.0.1:8000/docs` to test the analytical endpoints.

### Step B: The Orchestration (Automation)

Dagster manages the execution of the scraper, dbt models, and YOLO detection in the correct order.

```bash
dagster dev -f pipeline.py

```

* **Access UI**: Visit `http://127.0.0.1:3000`.
* **Run Pipeline**: Go to **Jobs** > **medical_warehouse_pipeline** > **Launchpad** > **Launch Run**.

---

## 5. Project Structure

```text
├── api/
│   ├── main.py          # FastAPI application
│   ├── schemas.py       # Pydantic data validation
│   └── database.py      # SQLAlchemy connection
├── medical_warehouse/   # dbt project folder
│   ├── models/          # SQL transformation models
│   └── dbt_project.yml
├── src/
│   ├── scraper.py       # Telegram scraping logic
│   ├── load_db.py       # Data loading to Postgres
│   └── yolo_detect.py   # YOLOv11 enrichment
├── pipeline.py          # Dagster orchestration definition
└── requirements.txt

```

---

## 6. Pipeline Workflow Summary

1. **Scrape**: Data is pulled from Telegram and saved as JSON.
2. **Load**: Raw JSON is moved into a PostgreSQL staging table.
3. **Transform**: dbt runs SQL models to build the Star Schema (Fact and Dimension tables).
4. **Enrich**: YOLOv11 detects objects in images and updates the analytical layer.
5. **Expose**: FastAPI queries the Fact tables to provide business insights.



