import os
import json
import psycopg2
from psycopg2.extras import execute_batch
from dotenv import load_dotenv

load_dotenv()

# Database Connection
def get_db_connection():
    return psycopg2.connect(
        dbname="medical_warehouse",
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host="localhost",
        port="5432"
    )

def load_all_jsons(root_dir):
    conn = get_db_connection()
    cur = conn.cursor()
    
    insert_query = """
        INSERT INTO raw.telegram_messages (msg_id, channel, date, text, views, forwards, media_path)
        VALUES (%(msg_id)s, %(channel)s, %(date)s, %(text)s, %(views)s, %(forwards)s, %(media_path)s)
        ON CONFLICT (msg_id, channel) DO NOTHING;
    """

    
    for subdir, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".json"):
                # Capture the Channel Name from filename
                channel_name = file.replace(".json", "")
                file_path = os.path.join(subdir, file)
                
                print(f"Processing: {channel_name} from {file_path}")
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    messages = json.load(f)
                    
                    # Add 'channel' key to every dictionary
                    for msg in messages:
                        msg['channel'] = channel_name
                    
                    # Insert
                    execute_batch(cur, insert_query, messages)
                    conn.commit()
    
    cur.close()
    conn.close()
    print("ALL DATA LOADED SUCCESSFULLY")

if __name__ == "__main__":
    load_all_jsons("data/raw/telegram_messages")
