import os
import logging
from telegram import Update, Voice
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from app.openai import transcribe_audio, chat_with_gpt
from app.notion import save_message, get_recent_history

load_dotenv(override=True)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TG_BOT_USERNAME = os.getenv("TG_BOT_USERNAME")
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def is_group_chat(update: Update) -> bool:
    return update.effective_chat.type in ["group", "supergroup"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"/start command from chat_id={update.effective_chat.id}, user_id={update.effective_user.id}")
    await update.message.reply_text("Hello! I'm your AI assistant. Send a text or voice message.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    chat_id = str(update.effective_chat.id)
    chat_type = update.effective_chat.type

    # Only reply in group/supergroup if bot is mentioned or message is reply to bot
    if chat_type in ["group", "supergroup"]:
        mentioned = False
        if TG_BOT_USERNAME:
            if TG_BOT_USERNAME in user_text:
                mentioned = True
        is_reply_to_bot = (
            update.message.reply_to_message and
            update.message.reply_to_message.from_user and
            TG_BOT_USERNAME and
            (update.message.reply_to_message.from_user.username == TG_BOT_USERNAME)
        )
        if not (mentioned or is_reply_to_bot):
            return  # Ignore non-mention, non-reply messages in group

    logger.info(f"Text message in chat_id={chat_id}: {user_text}")
    save_message(chat_id, user_text, raw_message=update.message.to_dict())
    history = get_recent_history(chat_id)
    # Build messages for GPT: all previous as user, last as user
    gpt_messages = [{"role": "user", "content": h["content"]} for h in history] + [{"role": "user", "content": user_text}]
    reply = chat_with_gpt(gpt_messages)
    save_message(chat_id, reply, raw_message={"reply_to": user_text, "reply": reply})
    await update.message.reply_text(reply)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice: Voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)
    ogg_path = f"voice_{voice.file_id}.ogg"
    wav_path = f"voice_{voice.file_id}.wav"
    logger.info(f"Downloading voice message file_id={voice.file_id} to {ogg_path}")
    await file.download_to_drive(ogg_path)
    text = transcribe_audio(ogg_path, wav_path)
    logger.info(f"Transcribed voice to text: {text}")
    chat_id = str(update.effective_chat.id)
    save_message(chat_id, text, raw_message=update.message.to_dict())
    history = get_recent_history(chat_id)
    gpt_messages = [{"role": "user", "content": h["content"]} for h in history] + [{"role": "user", "content": text}]
    reply = chat_with_gpt(gpt_messages)
    save_message(chat_id, reply, raw_message={"reply_to": text, "reply": reply})
    await update.message.reply_text(f"🗣️ *You said:* {text}\n\n🤖 *ChatGPT says:* {reply}", parse_mode='Markdown')


def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    logger.info("Bot started. Waiting for messages...")
    app.run_polling()

if __name__ == "__main__":
    main()
