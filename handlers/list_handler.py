from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TimedOut
from database.doctors_db import list_all
import asyncio
import io
from typing import List, Tuple


async def _safe_send(update: Update, text: str, retries: int = 3, base_delay: float = 1.0):
    for attempt in range(1, retries + 1):
        try:
            await update.message.reply_text(text)
            return
        except TimedOut:
            if attempt == retries:
                raise
            await asyncio.sleep(base_delay * (2 ** (attempt - 1)))


async def list_doctors(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = list_all()
    if not data:
        await _safe_send(update, "⚠️ لا يوجد أطباء حالياً.")
        return

    header = "📋 *جميع الأطباء:*\n\n"
    # Build full text and chunk it; keep full_text as fallback
    entries: List[str] = []
    for n, p, s in data:
        entries.append(f"👨‍⚕️ {n}\n📞 {p}\n🏷️ {s}\n---------------------\n")

    full_text = header + "".join(entries)

    max_len = 4000
    chunk = header

    try:
        for entry in entries:
            if len(chunk) + len(entry) > max_len:
                await _safe_send(update, chunk)
                await asyncio.sleep(0.25)
                chunk = entry
            else:
                chunk += entry

        if chunk:
            await _safe_send(update, chunk)

    except TimedOut:
        # Fallback: send the whole list as a .txt file to avoid many requests
        bio = io.BytesIO()
        bio.write(full_text.encode("utf-8"))
        bio.seek(0)
        filename = "doctors_list.txt"
        await update.message.reply_document(document=bio, filename=filename)