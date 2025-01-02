import telebot
from mytoken import get_bot_token
from function import setup_handlers

# Główna inicjalizacja bota
bot = telebot.TeleBot(get_bot_token())

# Ustawienie handlerów
setup_handlers(bot)

if __name__ == "__main__":
    print("Bot is running...")
    bot.polling()
