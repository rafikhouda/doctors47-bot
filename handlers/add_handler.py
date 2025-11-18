from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database.doctors_db import add_doctor
from config import ADMIN_IDS

NAME, PHONE, SPECIALTY, MUNICIPALITY = range(4)

# قائمة البلديات
MUNICIPALITIES = [
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
    context.user_data["specialty"] = update.message.text
    
    # عرض كيبورد البلديات
    keyboard = [[mun] for mun in MUNICIPALITIES]
    await update.message.reply_text(
        "📍 اختر البلدية:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return MUNICIPALITY

async def get_municipality(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = context.user_data["name"]
    phone = context.user_data["phone"]
    spec = context.user_data["specialty"]
    municipality = update.message.text

    add_doctor(name, phone, spec, municipality)

    await update.message.reply_text("✅ تم إضافة الطبيب بنجاح.")
    return ConversationHandler.END