from telegram import Update
import logging, os, json, requests
from telegram.ext import CommandHandler, ContextTypes,MessageHandler, Application,filters, ConversationHandler, CallbackQueryHandler
from keyboards.reply import phone_markup
from keyboards.inline import keyboard_city, distric_keyboard, test_markup,finish_markup
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
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
    telegram_id = update.message.from_user.id
    r = requests.get(url+f'getuser/{telegram_id}')
    if r.status_code==200:
        await update.message.reply_text("Test klaviaturasini tanlang:", reply_markup=test_markup)
    else:
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
    await query.edit_message_text("Test klaviaturasini tanlang:", reply_markup=test_markup)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Jarayon bekor qilindi.")
    
    return ConversationHandler.END




async def ShablonButton(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    query.answer()
    
    url_template = url + 'test_template/'
    r_template = requests.get(url_template)
    data_template = r_template.json()
    
    context.user_data['question'] = data_template
    context.user_data['score'] = 0
    context.user_data['wrong_answer'] = 0
    
    first_question = data_template[0]
    text = f"{first_question['title']}\n" + "\n".join(
        [f"F{i+1}. {option['text']}" for i, option in enumerate(first_question['options'])]
    )
    
    keyboard = [
        [InlineKeyboardButton(f"F{i+1}", callback_data=f"F{i+1}:{i}") for i in range(4)]
    ]
    keyboard.append([InlineKeyboardButton('Testni yakunlash 🏁', callback_data='finish')])
    reply_keyboard = InlineKeyboardMarkup(keyboard)

    if query.data == 'shablon':
        await query.edit_message_text(text, reply_markup=reply_keyboard)


async def NextShablonTest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    query_data_id = int(query.data.split(':')[1]) 
    questions = context.user_data['question']
    current_question = questions[0]  
    correct_option = next((i for i, opt in enumerate(current_question['options']) if opt['is_correct']), None)
    
    text_with_indicators = f"{current_question['title']}\n"
    
    for i, option in enumerate(current_question['options']):
        if i == query_data_id:
            if i == correct_option:
                indicator = "✅"
                context.user_data['score'] += 1 
            else:
                indicator = "❌"
                context.user_data['wrong_answer']+=1
        elif i == correct_option:
            indicator = "✅" 
        else:
            indicator = "" 
        
        text_with_indicators += f"{indicator} F{i+1}. {option['text']}\n"
    
    await query.edit_message_text(text_with_indicators.strip())

    del questions[0]
    if questions:
        next_question = questions[0]
        next_text = f"{next_question['title']}\n" + "\n".join(
            [f"F{i+1}. {option['text']}" for i, option in enumerate(next_question['options'])]
        )
        
        keyboard = [
            [InlineKeyboardButton(f"F{i+1}", callback_data=f"F{i+1}:{i}") for i in range(4)]
        ]
        keyboard.append([InlineKeyboardButton('Testni yakunlash 🏁', callback_data='finish')])
        reply_keyboard = InlineKeyboardMarkup(keyboard)
        
        await query.message.reply_text(next_text, reply_markup=reply_keyboard)
    else:
        final_score = context.user_data['score']
        wrong_answer = context.user_data["wrong_answer"]
        await query.message.reply_text(f"Test tugadi! \nTog'ri javoblar: {final_score} \nNoto'g'ri javoblar:{wrong_answer}")
        del context.user_data['question']
        del context.user_data['score']
        del context.user_data['wrong_answer']


async def finish_test(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    # Get scores and display the result
    final_score = context.user_data.get('score', 0)
    wrong_answer = context.user_data.get("wrong_answer", 0)
    message_text = f"Test tugadi!\nTo'g'ri javoblar: {final_score}\nNoto'g'ri javoblar: {wrong_answer}"
    
    # Send the result message with the finish keyboard
    await query.edit_message_text(message_text, reply_markup=finish_markup)

async def handle_retry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("Qayta urinish boshlandi.")
    # Reset score or restart quiz logic here if needed

async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("Asosiy menuga qaytildi.", reply_markup=test_markup)
    # Add logic to navigate back to the main menu here

def main():
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
    app.add_handler(CallbackQueryHandler(ShablonButton, pattern='^(shablon)$'))
    app.add_handler(CallbackQueryHandler(NextShablonTest, pattern='^(F1:0|F2:1|F3:2|F4:3)$'))
    app.add_handler(CallbackQueryHandler(finish_test, pattern='^finish$'))
    app.add_handler(CallbackQueryHandler(handle_retry, pattern='^retry$'))
    app.add_handler(CallbackQueryHandler(handle_main_menu, pattern='^main_menu$'))

    app.run_polling()

if __name__ == "__main__":
    main()