
import os
import csv
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.environ.get("BOT_TOKEN")
SHEET_CSV_URL = os.environ.get("SHEET_CSV_URL")  # Published CSV link

async def check_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message

    target_id = None
    if msg.forward_from:
        target_id = msg.forward_from.id
    elif msg.forward_from_chat:
        target_id = msg.forward_from_chat.id

    if not target_id:
        await msg.reply_text(
            "⚠️ I couldn't detect the original sender's ID.\n"
            "Ask them to send a message again, then forward it here."
        )
        return

    try:
        r = requests.get(SHEET_CSV_URL, timeout=5)
        r.raise_for_status()
        lines = r.text.splitlines()
        reader = csv.DictReader(lines)
        users = list(reader)
    except Exception:
        await msg.reply_text("⚠️ Error accessing verification list. Try again later.")
        return

    for row in users:
        if str(row.get("telegram_id", "")).strip() == str(target_id):
            status = row.get("status", "").lower()
            if status == "verified":
                await msg.reply_text(
                    f"✅ *Verified User*\n"
                    f"Telegram ID: `{target_id}`\n"
                    f"Status: Verified",
                    parse_mode="Markdown"
                )
                return
            else:
                await msg.reply_text(
                    f"❌ Not Verified\nTelegram ID: {target_id}"
                )
                return

    await msg.reply_text(
        f"❌ Not Verified\nTelegram ID: {target_id}\nUser not found in database."
    )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, check_user))
    app.run_polling()

if __name__ == "__main__":
    main()
