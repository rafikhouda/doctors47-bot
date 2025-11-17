from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from database.doctors_db import search, get_specialties
from handlers.start_handler import MAIN_MENU
from typing import List

async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    # Global cancel: if the user sends 'إلغاء' at any time, return to main menu
    if query == "إلغاء":
        context.user_data.pop("awaiting_search", None)
        context.user_data.pop("search_kind", None)
        await update.message.reply_text("أنت في الصفحة الرئيسية", reply_markup=ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True))
        return

    # If we were waiting for a search input (triggered by a menu button), clear the flag
    context.user_data.pop("awaiting_search", None)
    context.user_data.pop("search_kind", None)

    results = search(query)

    if not results:
        await update.message.reply_text("❌ لم يتم العثور على نتائج.")
        return

    text = "🔎 *نتائج البحث:*\n\n"
    for n, p, s in results:
        text += f"👨‍⚕️ *الاسم:* {n}\n📞 {p}\n🏷️ {s}\n---------------------\n"

    await update.message.reply_text(text)


async def start_search_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ask the user to enter a name to search
    context.user_data["awaiting_search"] = True
    context.user_data["search_kind"] = "name"
    await update.message.reply_text("🔎 أدخل اسم الطبيب للبحث:")


async def start_search_specialty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Present the list of specialties as buttons so the user can choose
    context.user_data["awaiting_search"] = True
    context.user_data["search_kind"] = "specialty"

    specialties: List[str] = get_specialties()
    if not specialties:
        await update.message.reply_text("⚠️ لا توجد تخصصات في القائمة بعد.")
        return

    # Build keyboard with 2 columns per row
    keyboard: List[List[str]] = []
    row = []
    for i, spec in enumerate(specialties, start=1):
        row.append(spec)
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    # Add cancel button
    keyboard.append(["إلغاء"])

    await update.message.reply_text(
        "🔎 اختر التخصص أو اكتب تَخصُّصًا:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    )