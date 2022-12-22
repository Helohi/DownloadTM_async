from threading import Thread

from bot.bot import Bot
from bot.handler import BotButtonCommandHandler, MessageHandler

from Buttons import answer
from distributor import dist
from functions import log
from Constance import TOKEN


# Creating bot
def main():
    bot = Bot(token=TOKEN)

    # Correct options in bot
    bot.dispatcher.add_handler(MessageHandler(callback=dist))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=answer))
    bot.start_polling()

    log('Start idle')
    bot.idle()


if __name__ == '__main__':
    main()
