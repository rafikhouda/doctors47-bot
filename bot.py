from telegram.ext import Application, MessageHandler, CommandHandler, ConversationHandler, filters
from config import BOT_TOKEN
from database.doctors_db import init_db

from handlers.start_handler import start, info_handler, myid, export_doctors, delete_doctor_cmd
from handlers.search_handler import handle_search, start_search_name, start_search_specialty
from handlers.list_handler import list_doctors
from handlers.add_handler import (
    start_add, get_name, get_phone, get_specialty,
    NAME, PHONE, SPECIALTY
)

def main():
    init_db()

    # Note: some telegram versions don't expose `Request` for import; keep default request
    app = Application.builder().token(BOT_TOKEN).build()

    # ConversationHandler — لإضافة الأطباء
    add_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(r"^(?:\+|➕) إضافة طبيب$"), start_add)],
        states={
            NAME: [MessageHandler(filters.TEXT, get_name)],
            PHONE: [MessageHandler(filters.TEXT, get_phone)],
            SPECIALTY: [MessageHandler(filters.TEXT, get_specialty)],
        },
        fallbacks=[],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(add_conv)

    # Menu button handlers (registered before the generic TEXT handler)
    app.add_handler(MessageHandler(filters.Regex(r"^🔍 بحث بالاسم$"), start_search_name))
    app.add_handler(MessageHandler(filters.Regex(r"^🔍 بحث بالتخصص$"), start_search_specialty))
    app.add_handler(MessageHandler(filters.Regex(r"^📋 جميع الأطباء$"), list_doctors))
    app.add_handler(MessageHandler(filters.Regex(r"^ℹ️ معلومات البوت$"), info_handler))

    # Admin commands
    app.add_handler(CommandHandler("myid", myid))
    app.add_handler(CommandHandler("export_doctors", export_doctors))
    app.add_handler(CommandHandler("delete_doctor", delete_doctor_cmd))

    # Fallback: any other text is treated as a search query
    app.add_handler(MessageHandler(filters.TEXT, handle_search))

    print("🤖 البوت يعمل الآن...")
    app.run_polling()

if __name__ == "__main__":
    main()
