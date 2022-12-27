# from multiprocessing import Process
from os import remove
from os.path import basename, getsize
from re import findall
from sys import argv
from threading import Thread
from time import time

from bot.bot import Bot

from Constance import (ERROROCCURE, HELLO, NOSPAM, PAY,
                       NOVIDEOQUALITY, TOKEN)
from functions import (check_server_clearness, choose_quality, google_search,
                       in_channel, install_youtube, is_data_wrong, links, log,
                       multiproc, print_bot, print_bot_button)
from googleapi import check_drive, upload_file

in_process, started, to_start = set(), [], dict()
# Developer functions
if len(argv) > 1:
    only_admin = True
    log('Only admin')
else:
    only_admin = False
    log('All users allowed')


def dist(bot, event):
    """ First checking """
    log("Got new message")
    # Checking for spamming
    if event.from_chat in in_process:
        log(f"Spamming {event.from_chat}  {event.data['from']['firstName']}")
        print_bot(NOSPAM, bot, event.from_chat)
        return None
    elif (chat := event.data["chat"]["type"]) == 'group' or chat == "channel":
        return None
    elif answer := is_data_wrong(event.text):
        print_bot(answer, bot, event.from_chat)
        return None
    # Only in channel users can use this bot. Checking that. , channel_id="686294615@chat.agent"
    elif in_channel(bot, event.from_chat, channel_id="686692940@chat.agent") is False:
        log(f"Not subscribed {event.from_chat}, {event.data['from']['nick']}, {event.data['from']['firstName']}")
        print_bot_button(bot, event.from_chat, text=PAY,
                         url=True, Buy='https://web.icq.com/chat/alexmoon')
        return None

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

    main_functions(bot, event, is_admin)


@multiproc
def main_functions(bot, event, is_admin: bool = False):
    """ Second Checking """
    # Handling basic commands
    if event.text.strip() == '/start' or event.text.strip() == '/help':
        print_bot(text=HELLO, bot=bot, user_id=event.from_chat)
        return None
    elif event.text.strip() == '/queue':
        log('/queue: ', event.from_chat, event.data['from']['nick'])
        print_bot(text=f'You get new Achivement: The rarest man in bot! Respect!',
                  bot=bot, user_id=event.from_chat)
        return None

    in_process.add(event.from_chat)  # One user - one request
    to_start[event.from_chat] = (event, is_admin,)
    return None


def team_leader(bot):
    global started
    while True:
        try:
            if to_start:
                if not in_process:
                    check_server_clearness()
                check_drive()
                for id in to_start.copy():
                    process_ = Thread(target=worker,
                                      args=(bot,
                                            to_start[id][0],
                                            to_start[id][1]),
                                      daemon=True)
                    to_start.pop(id)
                    process_.start()
                    started.append((time(), process_, id))
                    log(f"{len(started)} processes running")
        except BaseException as err:
            # If chought an unexpected error
            log(f"Error in team_leader: {type(err)}, {err}")
            for user in in_process:
                print_bot(ERROROCCURE, Bot(TOKEN), user)
            in_process.clear()
            to_start.clear()
    return


def worker(bot, event, is_admin: bool = False):
    """ The main things happen here """
    log(f"From: {event.from_chat}, "
        f"{event.data['from']['firstName'] if 'firstName' in event.data['from'] else None}, "
        f"{event.data['from']['nick'] if 'nick' in event.data['from'] else 'None'}. "
        f"Message: {event.text}")
    # If Links(take too much resources to be at start)
    if event.text.strip() == "/links":
        lst_ = links()  # (text_to_send, buttons)
        lst = lst_
        print_bot_button(bot, event.from_chat, lst[0],
                         True, lst[1])
        in_process.remove(
            event.from_chat) if event.from_chat in in_process else print(end="")
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
            print_bot_button(bot, event.from_chat, text_,
                             buttons=buttons, is_admin=is_admin)
            in_process.remove(
                event.from_chat) if event.from_chat in in_process else print(end="")
            return None

        url = event.text.replace(f'-{opt}-', '').strip()
        log(f"Downloading video to server")

        print_bot(f'url:<i>{url}</i>\n with quality:<b>{opt}</b>\n'
                  'Start downloading...', bot, event.from_chat)

        path = list((None,))
        proc_ = Thread(target=install_youtube, kwargs={"url": url, "res": opt,
                                                       "audio": True if opt == 'audio' else None, "return_list": path})
        proc_.start()
        proc_.join()
        path = path[-1]

        if path is None:  # No such video quality
            print_bot(NOVIDEOQUALITY, bot=bot, user_id=event.from_chat)
            in_process.remove(
                event.from_chat) if event.from_chat in in_process else print(end="")
            return

        elif path == 'Space':  # No space on server
            print_bot('Not enough space on server, please try later!',
                      bot, event.from_chat)
            print_bot('Clear me!', bot, user_id='705079793')
            in_process.remove(
                event.from_chat) if event.from_chat in in_process else print(end="")
            return

        proc_ = Thread(target=sending_video, args=(bot, event, path))
        proc_.start()
        proc_.join()
        check_drive()

    else:  # Not link to youtube video
        print_bot(
            text=f'I\'m searching <b>{event.text}</b> on youtube:',
            bot=bot, user_id=event.from_chat)

        lang = 'en'
        for char in ['-ru-', '-en-']:
            if char in event.text:
                lang = char.strip('-')
        try:
            rtn_lst = list((None, None,))
            proc_ = Thread(target=google_search, kwargs={
                "query": event.text, "lang": lang, "is_admin": only_admin, "return_list": rtn_lst})
            proc_.start()
            proc_.join()
            text, buttons = rtn_lst[-2], rtn_lst[-1]
            if not buttons:
                print_bot(text='No results found',
                          bot=bot, user_id=event.from_chat)
            else:
                print_bot_button(bot, user_id=event.from_chat,
                                 text=text, buttons=buttons)
            in_process.remove(
                event.from_chat) if event.from_chat in in_process else print(end="")
        except BaseException as err:
            print_bot('Error with <i>Google search</i>, pls try <b>later</b>',
                      bot, user_id=event.from_chat)
            log('Error with Google search', type(err), err)
            in_process.remove(
                event.from_chat) if event.from_chat in in_process else print(end="")
            return None
    return None


@multiproc
def sending_video(bot, event, path, only_gd: bool = False, chat: bool = False):
    """ Function for sending video """
    log(f"In function -> sending video")
    if only_gd or getsize(path) > 40_000_000:  # By Google drive
        log("Sending by google drive")
        try:
            link = list((None,))
            proc_ = Thread(target=upload_file, kwargs={
                           "path": path, "title": basename(path), "return_list": link})
            proc_.start()
            proc_.join()
            link = link[-1]
        except BaseException as err:
            print_bot('Error with <i>google drive</i>, pls try again <b>later</b>',
                      bot=bot, user_id=event.from_chat)
            log('Error with Google Drive:', type(err), err)
        else:
            print_bot_button(text=f'I did it! Link:\n{link} ', bot=bot,
                             user_id=event.from_chat, url=[True, False], Link=link,
                             Delete=f"delete:{basename(path)}")
        finally:
            log("Removing video from server")
            remove(path)
            in_process.remove(
                event.from_chat) if event.from_chat in in_process else print(end="")
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
                sending_video(bot, event, path, only_gd=True)
                break
            else:
                in_process.remove(
                    event.from_chat) if event.from_chat in in_process else print(end="")
                log("Removing video from server")
                remove(path)
                break
        else:
            sending_video(bot, event, path, only_gd=True)
    return None


if __name__ == '__main__':
    log('Everything working correct')
    # Event(type='EventType.NEW_MESSAGE', data='{'chat': {'chatId': '686692940@chat.agent', 'title': 'TeztTM', 'type': 'group'}, 'from': {'firstName': 'Helo_hi', 'nick': 'tm_team.', 'userId': '705079793'}, 'msgId': '7165877329619583046', 'text': 'test -admin-', 'timestamp': 1668435831}')
