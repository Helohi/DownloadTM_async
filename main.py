from threading import Thread

from bot.bot import Bot
from bot.handler import BotButtonCommandHandler, MessageHandler

from Buttons import answer
from Constance import TOKEN
from distributor import dist, team_leader
from functions import check_for_overtime, log


# Creating bot
def main():
    bot = Bot(token=TOKEN)

    # Correct options in bot
    bot.dispatcher.add_handler(MessageHandler(callback=dist))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=answer))
    bot.start_polling()

    # Team_leader runer
    Thread(target=team_leader, args=(bot,), daemon=True).start()
    Thread(target=check_for_overtime, args=(bot,), daemon=True).start()
    log("team_leader run")

    log('Start idle')
    bot.idle()


if __name__ == '__main__':
    main()
