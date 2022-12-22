from sys import argv
from multiprocessing import Process

from Constance import NOSPAM
from functions import choose_quality, log, print_bot, print_bot_button, multiproc
from googleapi import delete_one_file
import distributor as dr

def answer(bot, event):
    answer_callback(bot, event)

    is_admin = False
    if len(argv) > 1 and not '-admin-' in event.callback_query:  # Not allowed to session
        return None
    elif not len(argv) > 1 and '-admin-' in event.callback_query:  # Not to us
        return None
    else:
        if '-admin-' in event.callback_query:
            is_admin = True
            event.callback_query = event.callback_query.replace('-admin-', '')

    log('Got callback from button')

    if 'delete:' in (data := event.callback_query):
        delete_one_file(file_name=data.lstrip('delete:'))
        print_bot("<b>Thank you</b> for saving memory!👍❤",
                  bot, event.from_chat)
        return

    elif 'download:' in (data := event.callback_query):
        if event.from_chat in dr.in_process:
            print_bot(NOSPAM, bot, event.from_chat)
            return None
        else:
            dr.in_process.append(event.from_chat)

        event.text = data.strip('download:')
        dr.main_functions(bot, event, is_admin)
        log("Send requests and Im free")
        return None

    else:
        text_, buttons = choose_quality(event.callback_query)
        print_bot_button(text=text_, bot=bot,
                         user_id=event.from_chat, buttons=buttons)
        return


@multiproc
def answer_callback(bot, event):
    bot.answer_callback_query(
        query_id=event.data['queryId'],
        text="Got it!",
        show_alert=False
    )
