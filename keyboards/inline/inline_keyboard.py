from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import json

with open('data.json', 'r') as file:
    data = json.load(file)


city, distric = data['city'], data['distric']
keyboard = []
for i in range(0, len(city), 2):
    row = [
        InlineKeyboardButton(city[i]['name'], callback_data=f"{city[i]['id']}:{city[i]['name']}")
    ]
    if i + 1 < len(city):
        row.append(InlineKeyboardButton(city[i + 1]['name'], callback_data=f"{city[i + 1]['id']}:{city[i + 1]['name']}"))
    keyboard.append(row)



keyboard_test = [
    [InlineKeyboardButton('Shablon test', callback_data='shablon'),InlineKeyboardButton('Imtihon ishlash', callback_data='test')]
]
test_markup = InlineKeyboardMarkup(keyboard_test)

finish_keyboard = [
    [InlineKeyboardButton('Qayta urinish ↩️', callback_data='retry'), 
     InlineKeyboardButton('Asosiy menuga ➡️', callback_data='main_menu')]
]
finish_markup = InlineKeyboardMarkup(finish_keyboard)
def distric_keyboard(distric_callback):
    rows = []
    row = []
    for i in distric:
        if int(distric_callback) == int(i['region_id']):
            row.append(InlineKeyboardButton(i['name'], callback_data=f"{i['id']}:{i['name']}"))
            if len(row) == 2:
                rows.append(row)
                row = []
    if row:
        rows.append(row)

    if not rows:
        print("Warning: No districts found for the given region_id.")
        return None

    return InlineKeyboardMarkup(rows)



keyboard_city = InlineKeyboardMarkup(keyboard)