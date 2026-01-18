import os
import json
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Optional
from telethon import TelegramClient, errors

from utils import setup_logger

load_dotenv()
API_ID = os.getenv('APP_API_ID')
API_HASH = os.getenv('APP_API_HASH')


logger = setup_logger()

class TelegramMessage(BaseModel):
    msg_id: int
    date: str
    text: Optional[str] = ""
    views: Optional[int] = 0
    forwards: Optional[int] = 0
    media_path: Optional[str] = None


async def scrape_channel(client, channel_link, bouncer):
    async with bouncer:
        channel_name = channel_link.split('/')[-1].replace('@', '')
        logger.info(f"PROCEEDING: Scraping all messages from {channel_name}")
        
        scraped_data = []
        
        try:
            # Iterating through 1000 messages
            async for message in client.iter_messages(channel_link, limit=1000):
                # Extraction
                msg_obj = TelegramMessage(
                    msg_id=message.id,
                    date=str(message.date),
                    text=message.text or "",
                    views=message.views or 0,
                    forwards=message.forwards or 0
                )

                if message.photo:
                    image_dir = f"data/raw/images/{channel_name}"
                    os.makedirs(image_dir, exist_ok=True)
                    img_path = f"{image_dir}/{message.id}.jpg"
                    
                    # Download only if file doesn't exist
                    if not os.path.exists(img_path):
                        await client.download_media(message.photo, file=img_path)
                    msg_obj.media_path = img_path

                scraped_data.append(msg_obj.model_dump())

                await asyncio.sleep(0.1) 
                
                if len(scraped_data) % 50 == 0:
                    logger.info(f"[{channel_name}] Progress: {len(scraped_data)} messages collected.")

            save_to_data_lake(channel_name, scraped_data)

        except errors.FloodWaitError as e:
            logger.error(f"FLOOD: Must wait {e.seconds}s for {channel_name}")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            logger.error(f"CRASH in {channel_name}: {e}", exc_info=True)

def save_to_data_lake(channel_name, data):
    # Partition by YYYY-MM-DD
    date_partition = datetime.now().strftime('%Y-%m-%d')
    output_dir = f"data/raw/telegram_messages/{date_partition}"
    os.makedirs(output_dir, exist_ok=True)
    
    file_path = f"{output_dir}/{channel_name}.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    logger.info(f"SUCCESS: Saved {len(data)} messages to {file_path}")

async def main():
    async with TelegramClient('scraper_session', API_ID, API_HASH) as client:
        bouncer = asyncio.Semaphore(2) # Only 2 channels at once
        channel_links = [
            'https://t.me/CheMed123',
            'https://t.me/lobelia4cosmetics',
            'https://t.me/tikvahpharma'
        ]
        
        tasks = [scrape_channel(client, link, bouncer) for link in channel_links]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
