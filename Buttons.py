from sys import argv
import asyncio

from Constance import NOSPAM
from functions import log, print_bot, print_bot_button, choose_quality
from googleapi import delete_one_file


def run_answer(bot, event):
    asyncio.run(answer(bot, event))


async def answer(bot, event):
    await asyncio.create_task(answer_callback(bot, event))

    is_admin = False
    if len(argv) > 0 and not '-admin-' in event.callback_query:  # Not allowed to session
        return None
    elif not len(argv) > 0 and '-admin-' in event.callback_query:  # Not to us
        return None
    else:
        if '-admin-' in event.callback_query:
            is_admin = True
            event.callback_query = event.callback_query.replace('-admin-', '')

    log('Got callback from button')

    if 'delete:' in (data := event.callback_query):
        await asyncio.create_task(delete_one_file(file_name=data.lstrip('delete:')))
        await asyncio.create_task(print_bot("<b>Thank you</b> for saving memory!👍❤",
                                            bot, event.from_chat))
        return

    elif 'download:' in (data := event.callback_query):
        from distributor import queue

        if event.from_chat in queue:
            print_bot(NOSPAM, bot, event.from_chat)
            return None

        event.text = data.strip('download:')
        if queue:
            await asyncio.create_task(print_bot(
                f'Got it! You added to queue ({len(queue)})\nВы добавлены в очередь ({len(queue)})',
                bot, event.from_chat))
        queue[event.from_chat] = (event, is_admin,)

    else:
        text_, buttons = await asyncio.create_task(
            choose_quality(event.callback_query))
        await asyncio.create_task(
            print_bot_button(text=text_,
                bot=bot, user_id=event.from_chat, buttons=buttons))
        return


async def answer_callback(bot, event):
    bot.answer_callback_query(
        query_id=event.data['queryId'],
        text="Got it!",
        show_alert=False
    )
