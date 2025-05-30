# AI-in-TG: Telegram ChatGPT Bot with Notion Memory

## Features
- Group-ready Telegram bot (text & voice)
- Uses OpenAI GPT-4 & Whisper
- Saves and retrieves chat memory from Notion

## Setup
1. Clone repo & install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and fill in your API keys.
3. Run the bot:
   ```bash
   python bot.py
   ```

## Files
- `bot.py` – Main bot logic
- `openai_client.py` – OpenAI API/Whisper helpers
- `notion_client.py` – Notion memory helpers

## Deployment
- Ready for Render, Railway, or any cloud

---

Contributions & issues welcome!
