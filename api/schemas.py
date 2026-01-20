from pydantic import BaseModel
from typing import List, Optional

# For Top Products
class ProductStat(BaseModel):
    product_name: str
    mention_count: int

# For Channel Activity
class ChannelActivity(BaseModel):
    channel_name: str
    total_messages: int
    media_count: int

# For Message Search
class MessageResult(BaseModel):
    message_id: int
    message_text: Optional[str]
    channel_name: str
    date_key: int

# For Visual Content Stats
class VisualStats(BaseModel):
    image_category: str
    total_count: int
    avg_confidence: float
