from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
import io
from database.doctors_db import list_all, delete_doctor
from config import ADMIN_IDS
from database.doctors_db import add_doctor
import typing
from telegram import Document

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


async def import_doctors_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin-only: import doctors from a text file (same format as /export_doctors).
    Usage: send the file as a document with caption `/import_doctors`.
    """
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("⛔ لا تملك صلاحية الاستيراد.")
        return

    # Check if there's a document attached
    if not update.message.document:
        await update.message.reply_text("📤 أرسل ملف النص (doctors_list.txt) كمستند مرفق مع الأمر /import_doctors.\n\nمثال: أرسل الملف مع Caption: /import_doctors")
        return

    try:
        doc = update.message.document
        
        # Download the document
        file = await context.bot.get_file(doc.file_id)
        bio = io.BytesIO()
        await file.download(out=bio)
        bio.seek(0)
        text = bio.read().decode("utf-8", errors="ignore")

        # Parse entries
        imported = 0
        lines = [l.strip() for l in text.splitlines()]
        
        i = 0
        while i < len(lines):
            line = lines[i]
            # Look for a doctor name line (starts with the doctor emoji)
            if line.startswith("👨‍⚕️"):
                name = line.replace("👨‍⚕️", "", 1).strip()
                phone = ""
                spec = ""
                
                # Check next two lines for phone and specialty
                if i + 1 < len(lines) and lines[i+1].startswith("📞"):
                    phone = lines[i+1].replace("📞", "", 1).strip()
                if i + 2 < len(lines) and lines[i+2].startswith("🏷️"):
                    spec = lines[i+2].replace("🏷️", "", 1).strip()

                # Add doctor if all fields are present
                if name and phone and spec:
                    add_doctor(name, phone, spec)
                    imported += 1
                    i += 3
                else:
                    i += 1
            else:
                i += 1

        await update.message.reply_text(f"✅ اكتمال الاستيراد. تم استيراد {imported} طبيب(أطباء).")
    
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ أثناء الاستيراد: {str(e)}")