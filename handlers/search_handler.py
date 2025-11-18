from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from database.doctors_db import search, get_specialties, add_doctor
from handlers.start_handler import MAIN_MENU
from config import ADMIN_IDS
from typing import List
import io

# قائمة البلديات
MUNICIPALITIES = [
    "جميع البلديات",
    "منصورة",
    "غرداية",
    "ضاية بن ضحوة",
    "متليلي",
    "القرارة",
    "العطف",
    "زلفانة",
    "سبسب",
    "بونورة",
    "بريان"
]

async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    # Global cancel: if the user sends 'إلغاء' at any time, return to main menu
    if query == "إلغاء":
        context.user_data.pop("awaiting_search", None)
        context.user_data.pop("search_kind", None)
        context.user_data.pop("selected_municipality", None)
        await update.message.reply_text("أنت في الصفحة الرئيسية", reply_markup=ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True))
        return

    # If we were waiting for a search input (triggered by a menu button), clear the flag
    context.user_data.pop("awaiting_search", None)
    search_kind = context.user_data.pop("search_kind", None)
    
    # للبحث حسب البلدية
    if search_kind == "municipality":
        context.user_data["selected_municipality"] = query
        await update.message.reply_text("🔎 أدخل اسم الطبيب أو التخصص للبحث في البلدية المختارة:")
        context.user_data["awaiting_search"] = True
        return

    # للبحث العادي
    municipality = context.user_data.pop("selected_municipality", None)
    results = search(query, municipality)

    if not results:
        await update.message.reply_text("❌ لم يتم العثور على نتائج.")
        return

    text = "🔎 *نتائج البحث:*\n\n"
    for n, p, s, m in results:
        text += f"👨‍⚕️ *الاسم:* {n}\n📞 {p}\n🏷️ {s}\n📍 {m}\n---------------------\n"

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


async def start_search_municipality(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # عرض كيبورد البلديات
    context.user_data["awaiting_search"] = True
    context.user_data["search_kind"] = "municipality"
    
    keyboard = [[mun] for mun in MUNICIPALITIES]
    keyboard.append(["إلغاء"])
    await update.message.reply_text(
        "🔎 اختر البلدية:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    )


async def handle_document_import(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle document uploads for import_doctors command."""
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("⛔ لا تملك صلاحية الاستيراد.")
        return

    if not update.message.document:
        return

    try:
        doc = update.message.document
        file = await context.bot.get_file(doc.file_id)
        
        # استخدم download_to_memory مع BytesIO
        bio = io.BytesIO()
        await file.download_to_memory(out=bio)
        bio.seek(0)
        text = bio.read().decode("utf-8", errors="ignore")

        imported = 0
        lines = [l.strip() for l in text.splitlines()]

        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith("👨‍⚕️"):
                name = line.replace("👨‍⚕️", "", 1).strip()
                phone = ""
                spec = ""
                municipality = ""

                if i + 1 < len(lines) and lines[i + 1].startswith("📞"):
                    phone = lines[i + 1].replace("📞", "", 1).strip()
                if i + 2 < len(lines) and lines[i + 2].startswith("🏷️"):
                    spec = lines[i + 2].replace("🏷️", "", 1).strip()
                if i + 3 < len(lines) and lines[i + 3].startswith("📍"):
                    municipality = lines[i + 3].replace("📍", "", 1).strip()

                if name and phone and spec:
                    add_doctor(name, phone, spec, municipality)
                    imported += 1

            i += 1

        await update.message.reply_text(f"✅ تم استيراد {imported} طبيب(أطباء).")

    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {str(e)}")