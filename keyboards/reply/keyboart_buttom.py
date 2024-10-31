from telegram import KeyboardButton, ReplyKeyboardMarkup

keyboard = [[KeyboardButton("Telefon raqamni yuborish", request_contact=True)]]
phone_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

keyboard_test = [[KeyboardButton("shablon test")], [KeyboardButton("Imtihon ishlash")]]

test_markup = ReplyKeyboardMarkup(keyboard_test, resize_keyboard=True, one_time_keyboard=True)