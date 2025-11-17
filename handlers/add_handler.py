from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from database.doctors_db import add_doctor
from config import ADMIN_IDS

NAME, PHONE, SPECIALTY = range(3)

async def start_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return await update.message.reply_text("⛔ لا تملك صلاحية الإضافة.")
    
    await update.message.reply_text("📝 أدخل اسم الطبيب:")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("📞 أدخل رقم الهاتف:")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("🏷️ أدخل التخصص:")
    return SPECIALTY

async def get_specialty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = context.user_data["name"]
    phone = context.user_data["phone"]
    spec = update.message.text

    add_doctor(name, phone, spec)

    await update.message.reply_text("✅ تم إضافة الطبيب بنجاح.")
    return ConversationHandler.END