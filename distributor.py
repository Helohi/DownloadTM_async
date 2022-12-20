from os import remove
from os.path import basename, getsize
from re import findall
from sys import argv
import asyncio

from Constance import (HELLO, INQUEUE, MAIN_QUALITY, NOSPAM, NOTINCHANNEL,
                       NOVIDEOQUALITY)
from functions import (check_server_clearness, choose_quality,
                       google_search, in_channel, install_youtube,
                       is_data_wrong, links, log, print_bot, print_bot_button)
from googleapi import upload_file, check_drive

queue = dict()
# Developer functions
if len(argv) > 1:
    only_admin = True
    log('Only admin')
else:
    only_admin = False
    log('All users allowed')


def dist(bot, event):
    """ First checking """

    if event.from_chat in queue:
        print_bot(NOSPAM, bot, event.from_chat)
        return None
    elif answer := is_data_wrong(event.text):
        print_bot(answer, bot, event.from_chat)

    # Admin function logic
    is_admin = False
    if only_admin and not ('-admin-' in event.text):  # Not allowed to session
        return None
    elif not only_admin and ('-admin-' in event.text):  # Not to us
        return None
    else:
        if "-admin-" in event.text:
            is_admin = True
            event.text = event.text.replace('-admin-', '')

    asyncio.run(main_functions(bot, event, is_admin))


async def main_functions(bot, event, is_admin: bool = False):
    """ Second Checking """
    # Handling basic commands
    if event.text.strip() == '/start' or event.text.strip() == '/help':
        print_bot_task = asyncio.create_task(
            print_bot(text=HELLO, bot=bot, user_id=event.from_chat))
        await print_bot_task
        return None
    elif event.text.strip() == '/queue':
        print_bot_task = asyncio.create_task(
            print_bot(text=f'{len(queue)} in queue\n{len(queue)} в очереди',
                      bot=bot, user_id=event.from_chat))
        await print_bot_task
        return None

    # Only in channel users can use this bot. Checking that. , channel_id="686294615@chat.agent"
    if await in_channel(bot, event.from_chat, channel_id="686294615@chat.agent") is False:
        print_button_task = asyncio.create_task(
            print_bot_button(bot, event.from_chat, text=NOTINCHANNEL,
                             url=True, Channel='https://icq.im/TM_team'))
        await print_button_task
        return None

    if queue:
        print_bot_task = asyncio.create_task(
            print_bot(INQUEUE.format(len(queue),
                                     len(queue)), bot, event.from_chat))
        await print_bot_task
    queue[event.from_chat] = (event, is_admin,)


def TeamLeader(bot):
    """ Algorithm to work gradually, one by one """
    while 1:  # This thread is daemon, it will closed automatically when main will off
        if queue:  # To not write every time "Bot is ready"
            log('Bot start working')
            for user_id in queue.copy():  # Copy to not mess up list, while changing
                log(f'start working {user_id},'
                    f'{queue[user_id][0].data["from"]["firstName"]}.'
                    f'Message: {queue[user_id][0].text}')
                try:
                    # Sending to main algorithm
                    asyncio.run(worker(bot, queue[user_id][0],
                                       queue[user_id][1]))
                except BaseException as error:
                    log(type(error), error)
                finally:
                    asyncio.run(check_server_clearness())
                    # After finishing, we delete task from line list
                    queue.pop(user_id)
            else:
                log('Bot is ready')


async def worker(bot, event, is_admin: bool = False):
    """ The main things happen here """
    # If Links(take too much resources to be at start)
    if event.text.strip() == "/links":
        lst_ = asyncio.create_task(links())  # (text_to_send, buttons)
        lst = await lst_
        print_button_task = asyncio.create_task(
            print_bot_button(bot, event.from_chat, lst[0],
                             True, lst[1]))
        await print_button_task
        return

    # Checking url
    url_bool = False  # Is link to video
    for search in ['youtube', 'youtu.be']:
        if event.text.find(search) != -1:
            url_bool = True
            break

    if url_bool:
        # Preare of data
        if opt := findall('-[0-9]{3,4}-', event.text):  # If there is quality
            opt = int(opt[0].strip('-'))
        elif '-audio-' in event.text:
            opt = 'audio'
        else:
            opt = ''

        if not opt:  # Need quality
            text_, buttons = choose_quality(url=event.text)
            print_button_task = asyncio.create_task(
                print_bot_button(bot, event.from_chat, text_,
                                 buttons=buttons, is_admin=is_admin))
            await print_button_task
            return None

        url = event.text.replace(f'-{opt}-', '').strip()
        log(f"Downloading video to server")

        print_bot_task = asyncio.create_task(
            print_bot(f'url:<i>{url}</i>\n with quality:<b>{opt}</b>\n'
                      'Start downloading...', bot, event.from_chat))
        await print_bot_task

        install_task = asyncio.create_task(
            install_youtube(url=url, res=opt,
                            audio=True if opt == 'audio' else None))
        path = await install_task

        if path is None:  # No such video quality
            print_bot_task = asyncio.create_task(
                print_bot(NOVIDEOQUALITY,
                          bot=bot, user_id=event.from_chat))
            await print_bot_task
            return

        elif path == 'Space':  # No space on server
            print_bot_task = asyncio.create_task(
                print_bot('Not enough space on server, please try later!',
                          bot, event.from_chat))
            print_bot_task_ = asyncio.create_task(
                print_bot('Clear me!', bot, user_id='705079793'))
            await print_bot_task
            await print_bot_task_
            return

        sending_video_task = asyncio.create_task(
            sending_video(bot, event, path))
        check_drive_task = asyncio.create_task(check_drive())
        await sending_video_task
        await check_drive_task

    else:  # Not link to youtube video
        print_bot_task = asyncio.create_task(print_bot(
            text=f'I\'m searching <b>{event.text}</b> on youtube:',
            bot=bot, user_id=event.from_chat))
        await print_bot_task

        lang = 'en'
        for char in ['-ru-', '-en-']:
            if char in event.text:
                lang = char.strip('-')
        try:
            google_search_task = asyncio.create_task(google_search(
                query=event.text, lang=lang, is_admin=only_admin))
            text, buttons = await google_search_task
            if not buttons:
                await asyncio.create_task(print_bot(text='No results found',
                                                    bot=bot, user_id=event.from_chat))
            else:
                await asyncio.create_task(
                    print_bot_button(bot, user_id=event.from_chat,
                                     text=text, buttons=buttons))
        except BaseException as err:
            await asyncio.create_task(print_bot('Error with <i>Google search</i>, pls try <b>later</b>',
                                                bot, user_id=event.from_chat))
            log('Error with Google search', type(err), err)
    return None


async def sending_video(bot, event, path, only_gd: bool = False, chat: bool = False):
    """ Function for sending video """
    log(f"In function -> sending video, chat:{chat}")
    if getsize(path) > 400_000_000 or only_gd:  # By Google drive
        log("Sending by google drive")
        try:
            link = await asyncio.create_task(upload_file(path=path, title=basename(path)))
        except BaseException as err:
            await asyncio.create_task(print_bot('Error with <i>google drive</i>, pls try again <b>later</b>',
                                                bot=bot, user_id=event.from_chat))
            log('Error with Google Drive:', type(err), err)
        else:
            await asyncio.create_task(print_bot_button(text=f'I did it! Link:\n{link} ', bot=bot,
                                                       user_id=event.from_chat, url=[True, False], Link=link,
                                                       Delete=f"delete:{basename(path)}"))
        finally:
            log("Removing video from server")
            await asyncio.create_task(remove(path))
    else:  # by ICQ
        log("Sending by icq")
        for _ in range(3):
            try:
                with open(path, 'rb') as file:
                    sended_file = bot.send_file(
                        chat_id=event.from_chat, file=file)
                    if sended_file.status_code != 200:
                        continue
            except BaseException as err:
                print(type(err), ':', err)
                await asyncio.create_task(
                    sending_video(bot, event, path, only_gd=True))
                break
            else:
                log("Removing video from server")
                await asyncio.create_task(remove(path))
                break
        else:
            await asyncio.create_task(sending_video(bot, event, path, only_gd=True))


if __name__ == '__main__':
    log('Everything working correct')
    # Event(type='EventType.NEW_MESSAGE', data='{'chat': {'chatId': '686692940@chat.agent', 'title': 'TeztTM', 'type': 'group'}, 'from': {'firstName': 'Helo_hi', 'nick': 'tm_team.', 'userId': '705079793'}, 'msgId': '7165877329619583046', 'text': 'test -admin-', 'timestamp': 1668435831}')
