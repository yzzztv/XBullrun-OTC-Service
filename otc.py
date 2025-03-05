import os
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")

# Database setup
conn = sqlite3.connect("orders.db")
cursor = conn.cursor()
cursor.execute(
    """CREATE TABLE IF NOT EXISTS users 
    (user_id INTEGER PRIMARY KEY, language TEXT)"""
)
cursor.execute(
    """CREATE TABLE IF NOT EXISTS orders 
    (id INTEGER PRIMARY KEY, user_id INTEGER, type TEXT, amount TEXT, wallet TEXT, payment_method TEXT, status TEXT)"""
)
conn.commit()

# Initialize bot
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Language dictionary
LANGUAGES = {
    "en": "English",
    "id": "Indonesia",
    "ng": "Nigeria",
    "ar": "العربية",
    "ir": "ایران",
    "in": "भारत",
    "ru": "Русский"
}

MESSAGES = {
    "choose_language": {
        "en": "Please select your language:",
        "id": "Silakan pilih bahasa Anda:",
        "ng": "Jọwọ yan ede rẹ:",
        "ar": "الرجاء تحديد لغتك:",
        "ir": "لطفاً زبان خود را انتخاب کنید:",
        "in": "कृपया अपनी भाषा चुनें:",
        "ru": "Пожалуйста, выберите ваш язык:"
    },
    "welcome": {
        "en": "Welcome to the XBullrun OTC Service Bot! Choose an option below:",
        "id": "Selamat datang di Bot XBullrun OTC Service! Pilih opsi di bawah:",
        "ng": "Kaabọ si Bot XBullrun OTC Service! Yan aṣayan ni isalẹ:",
        "ar": "مرحبًا بك في بوت XBullrun OTC Service! اختر خيارًا أدناه:",
        "ir": "به ربات XBullrun OTC Service خوش آمدید! یکی از گزینه‌های زیر را انتخاب کنید:",
        "in": "ओटीसी बॉट में आपका स्वागत है! नीचे एक विकल्प चुनें:",
        "ru": "Добро пожаловать в бот XBullrun OTC Service! Выберите вариант ниже:"
    }
}

# Keyboard for language selection
language_keyboard = InlineKeyboardMarkup()
for code, name in LANGUAGES.items():
    language_keyboard.add(InlineKeyboardButton(name, callback_data=f"set_lang_{code}"))


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    user_id = message.from_user.id
    cursor.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
    user_lang = cursor.fetchone()

    if user_lang:
        lang = user_lang[0]
        await message.reply(MESSAGES["welcome"][lang], reply_markup=main_menu(lang))
    else:
        await message.reply(MESSAGES["choose_language"]["en"], reply_markup=language_keyboard)


@dp.callback_query_handler(lambda c: c.data.startswith("set_lang"))
async def set_language(callback_query: types.CallbackQuery):
    lang_code = callback_query.data.split("_")[2]
    user_id = callback_query.from_user.id

    cursor.execute("INSERT OR REPLACE INTO users (user_id, language) VALUES (?, ?)", (user_id, lang_code))
    conn.commit()

    await bot.send_message(user_id, MESSAGES["welcome"][lang_code], reply_markup=main_menu(lang_code))


def main_menu(lang):
    return ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton("💰 Beli Crypto" if lang == "id" else "💰 Buy Crypto"),
        KeyboardButton("💱 Jual Crypto" if lang == "id" else "💱 Sell Crypto")
    )


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
