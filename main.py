from threading import Thread

from bot.bot import Bot
from bot.handler import BotButtonCommandHandler, MessageHandler

from Buttons import run_answer
from distributor import TeamLeader, dist
from functions import log


# Creating bot
def main():
    # TOKEN = "001.0860138766.2792244880:1007541821"
    TOKEN = "001.3036675131.1370245590:1007918545"
    bot = Bot(token=TOKEN)

    # Correct options in bot
    bot.dispatcher.add_handler(MessageHandler(callback=dist))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=run_answer))
    bot.start_polling()

    # Start function, that rule all program
    team_lid = Thread(target=TeamLeader, args=(bot,), daemon=True)
    team_lid.start()

    log('Start idle')
    bot.idle()


if __name__ == '__main__':
    main()
