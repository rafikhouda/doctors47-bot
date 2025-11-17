from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
import io
from database.doctors_db import list_all, delete_doctor
from config import ADMIN_IDS

MAIN_MENU = [
    ["🔍 بحث بالاسم", "🔍 بحث بالتخصص"],
    ["📋 جميع الأطباء", "➕ إضافة طبيب"],
    ["ℹ️ معلومات البوت"]
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 مرحبا بك في *بوت أطباء غرداية*\nاختر ما تريد:",
        reply_markup=ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)
    )


async def info_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ هذا بوت بسيط لإدارة قائمة الأطباء. يمكنك البحث عن الأطباء بالحرف أو بالتخصص، وإضافة أطباء (للمشرف)."
    )


async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Your id: {update.effective_user.id}")


async def export_doctors(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Only admins should call this; the check is done in bot registration
    data = list_all()
    header = "📋 جميع الأطباء:\n\n"
    full_text = header + "".join([f"👨‍⚕️ {n}\n📞 {p}\n🏷️ {s}\n---------------------\n" for n, p, s in data])

    bio = io.BytesIO()
    bio.write(full_text.encode("utf-8"))
    bio.seek(0)
    await update.message.reply_document(document=bio, filename="doctors_list.txt")


async def delete_doctor_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Admin-only command to delete a doctor by name
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("⛔ لا تملك صلاحية الحذف.")
        return
    
    if not context.args:
        await update.message.reply_text("استخدام: /delete_doctor <اسم الطبيب>")
        return
    
    doctor_name = " ".join(context.args)
    deleted_count = delete_doctor(doctor_name)
    
    if deleted_count > 0:
        await update.message.reply_text(f"✅ تم حذف الطبيب '{doctor_name}' بنجاح.")
    else:
        await update.message.reply_text(f"❌ لم يتم العثور على طبيب باسم '{doctor_name}'.")