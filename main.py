from telegram import Update
import logging, os, json, requests
from telegram.ext import CommandHandler, ContextTypes,MessageHandler, Application,filters, ConversationHandler, CallbackQueryHandler
from keyboards.reply import phone_markup
from keyboards.inline import keyboard_city, distric_keyboard, test_markup
from dotenv import load_dotenv
load_dotenv()
ASK_NAME, ASK_PHONE, ASK_CITY, ASK_DISTRIC = range(4)
url = 'http://127.0.0.1:8000//api/v1/'

with open('data.json', 'r') as file:
    data = json.load(file)

city, distric = data['city'], data['distric']

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"Salom To'liq ism sharifingizni kiriting:\nAbdullayev Abdulla Abdullayevich)")
    return ASK_NAME

async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['name'] = update.message.text
    
    await update.message.reply_text("Iltimos, telefon raqamingizni yuboring:", reply_markup=phone_markup)
    return ASK_PHONE

async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['phone_number'] = update.message.contact.phone_number
    context.user_data['telegram_id'] = update.message.from_user.id
    
    await update.message.reply_text("Yashash manzilingiz\n(Hududingizni tanlang)", reply_markup=keyboard_city)
    return ASK_CITY

async def ask_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    query = update.callback_query
    callback_data = query.data.split(':')[0]
    context.user_data['city'] = query.data.split(':')[1]
    if query:
        await query.edit_message_text(
            text="Yashash manzilingiz\n(Tumanni tanlang)",
            reply_markup=distric_keyboard(callback_data)
        )
    else:
        print("No callback query found")
    return ASK_DISTRIC


async def ask_distric(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    context.user_data['distric'] = query.data.split(':')[1]

    data = {
        "full_name": context.user_data['name'],
        "phone_number": context.user_data['phone_number'],
        "telegram_id": context.user_data['telegram_id'],
        "district": query.data.split(':')[1],
        "city": context.user_data['city']
    }
    r = requests.post(url+'person_add/', data=data)
    print(r.status_code, r.text)

    await query.edit_message_text("Test klaviaturasini tanlang:", reply_markup=test_markup)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Jarayon bekor qilindi.")
    
    return ConversationHandler.END


def main():
    # Bot uchun ilova yaratish
    app = Application.builder().token(os.getenv('BOT_TOKEN')).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
            ASK_PHONE: [MessageHandler(filters.CONTACT, ask_phone)],
            ASK_CITY: [CallbackQueryHandler(ask_city)],  # Callback handler
            ASK_DISTRIC: [CallbackQueryHandler(ask_distric)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    # Botni ishga tushirish
    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()