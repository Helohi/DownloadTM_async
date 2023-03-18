import tracemalloc

from bot.bot import Bot
from bot.handler import BotButtonCommandHandler, MessageHandler
from addition.Constance import TOKEN, TOKEN_admin
from addition.functions import log
from addition.UserMessage_class import UserMessage
from addition.UserButton_class import UserButtons


def create_bot_object():
    bot = Bot(token=TOKEN)
    return bot


def add_handlers(bot):
    bot.dispatcher.add_handler(MessageHandler(callback=UserMessage))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=UserButtons))
    bot.start_polling()


def main():
    bot = create_bot_object()
    add_handlers(bot)

    log("Starting idle")

    bot.idle()


if __name__ == "__main__":
    main()
