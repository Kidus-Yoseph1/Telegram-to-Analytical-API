from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from . import schemas, database

app = FastAPI(
    title="Medical Warehouse Analytical API",
    description="REST API to query dbt data marts for medical channel insights",
    version="1.0.0"
)

@app.get("/api/reports/top-products", response_model=List[schemas.ProductStat])
def get_top_products(limit: int = 10, db: Session = Depends(database.get_db)):
    """Returns the most frequently detected terms/products using YOLO results."""
    query = text("""
        SELECT detected_objects as product_name, COUNT(*) as mention_count
        FROM analytics.fct_image_detections
        GROUP BY detected_objects
        ORDER BY mention_count DESC
        LIMIT :limit
    """)
    result = db.execute(query, {"limit": limit})
    return result.all()


@app.get("/api/channels/{channel_name}/activity", response_model=schemas.ChannelActivity)
def get_channel_activity(channel_name: str, db: Session = Depends(database.get_db)):
    """Returns posting activity trends for a specific channel."""
    query = text("""
        SELECT 
            channel_name, 
            COUNT(message_id) as total_messages,
            SUM(CASE WHEN has_image = TRUE THEN 1 ELSE 0 END) as media_count
        FROM analytics.fct_messages m
        JOIN analytics.dim_channels c ON m.channel_key = c.channel_key
        WHERE c.channel_name = :channel_name
        GROUP BY channel_name
    """)
    result = db.execute(query, {"channel_name": channel_name}).first()
    if not result:
        raise HTTPException(status_code=404, detail="Channel not found")
    return result


@app.get("/api/search/messages", response_model=List[schemas.MessageResult])
def search_messages(query: str, limit: int = 20, db: Session = Depends(database.get_db)):
    """Searches for messages containing a specific keyword (e.g., paracetamol)."""
    sql_query = text("""
        SELECT m.message_id, m.message_text, c.channel_name, m.date_key
        FROM analytics.fct_messages m
        JOIN analytics.dim_channels c ON m.channel_key = c.channel_key
        WHERE m.message_text ILIKE :search_term
        LIMIT :limit
    """)
    result = db.execute(sql_query, {"search_term": f"%{query}%", "limit": limit})
    return result.all()


@app.get("/api/reports/visual-content", response_model=List[schemas.VisualStats])
def get_visual_content_stats(db: Session = Depends(database.get_db)):
    """Returns statistics about YOLO image classifications (e.g., product_listing vs promotional)."""
    query = text("""
        SELECT 
            image_category, 
            COUNT(*) as total_count, 
            ROUND(AVG(max_confidence)::numeric, 4) as avg_confidence
        FROM analytics.fct_image_detections
        GROUP BY image_category
    """)
    result = db.execute(query)
    return result.all()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
