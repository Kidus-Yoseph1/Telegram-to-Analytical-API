import subprocess
import os
from dagster import op, job, schedule, In


@op
def scrape_telegram_data():
    """Runs the Telegram scraping script."""
    subprocess.run(["python", "src/scraper.py"], check=True)
    return "Scraping Complete"

@op(ins={"start": In()}) 
def load_raw_to_postgres(start):
    """Loads JSON data from the scraper into PostgreSQL."""
    subprocess.run(["python", "src/load_db.py"], check=True)
    return "Data Loaded"

@op(ins={"start": In()})
def run_dbt_transformations(start):
    """Executes dbt models (stg, dim, fct)."""
    dbt_project_path = os.path.join(os.getcwd(), "medical_warehouse")
    
    try:
        subprocess.run(
            ["dbt", "run"], 
            cwd=dbt_project_path, 
            check=True
        )
        return "dbt Transformations Complete"
    except subprocess.CalledProcessError as e:
        print(f"dbt failed with return code {e.returncode}")
        raise e

@op(ins={"start": In()})
def run_yolo_enrichment(start):
    """Runs the YOLO object detection script."""
    subprocess.run(["python", "src/yolo_detect.py"], check=True)
    return "YOLO Enrichment Complete"

@job
def medical_warehouse_pipeline():
    scraped = scrape_telegram_data()
    loaded = load_raw_to_postgres(scraped)
    transformed = run_dbt_transformations(loaded)
    enriched = run_yolo_enrichment(transformed)

# Define the Schedule (Automation) 

@schedule(cron_schedule="0 0 * * *", job=medical_warehouse_pipeline)
def daily_medical_update():
    """Runs the entire pipeline every day at midnight."""
    return {}
