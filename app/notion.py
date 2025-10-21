import os
import json
from typing import Optional, List, Dict, Any
from notion_client import Client
from dotenv import load_dotenv

load_dotenv(override=True)
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
notion = Client(auth=NOTION_TOKEN)


print("NOTION_TOKEN:", NOTION_TOKEN)
print("NOTION_DATABASE_ID:", NOTION_DATABASE_ID)


def save_message(chat_id: str, content: str, raw_message: Optional[dict] = None) -> None:
    """
    Save a message to the Notion database with Chat ID, Message, and Raw fields.
    'Created At' is handled automatically by Notion.
    """
    properties = {
        "Chat ID": {"title": [{"text": {"content": chat_id}}]},
        "Message": {"rich_text": [{"text": {"content": content}}]}
    }
    if raw_message is not None:
        properties["Raw"] = {"rich_text": [{"text": {"content": json.dumps(raw_message, ensure_ascii=False)}}]}
    notion.pages.create(
        parent={"database_id": NOTION_DATABASE_ID},
        properties=properties
    )


def get_recent_history(chat_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Retrieve the most recent messages for a given Chat ID from Notion.
    Returns a list of dicts with 'content' (Message).
    """
    results = notion.databases.query(
        **{"database_id": NOTION_DATABASE_ID,
           "filter": {"property": "Chat ID", "title": {"equals": chat_id}},
           "sorts": [{"property": "Created At", "direction": "ascending"}]}
    )
    history = []
    for page in results.get('results', [])[-limit:]:
        props = page['properties']
        content = props['Message']['rich_text'][0]['plain_text']
        history.append({"content": content})
    return history
