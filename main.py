from bot.bot import Bot, Event
from bot.handler import BotButtonCommandHandler, MessageHandler
from addition.Constance import TOKEN, TOKEN_admin
from addition.functions import log
from addition.UserMessage_class import UserMessage
from addition.UserButton_class import UserButtons


def create_user_message_var(bot: Bot, event: Event):
    UserMessage(bot, event)


def create_user_button_var(bot: Bot, event: Event):
    UserButtons(bot, event)


def create_bot_object():
    bot = Bot(token=TOKEN)
    return bot


def add_handlers(bot):
    bot.dispatcher.add_handler(MessageHandler(callback=create_user_message_var))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=create_user_button_var))
    bot.start_polling()


def main():
    bot = create_bot_object()
    add_handlers(bot)

    log("Starting idle")

    bot.idle()


if __name__ == "__main__":
    main()
