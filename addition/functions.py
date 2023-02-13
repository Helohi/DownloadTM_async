import json
import logging
import os
from os import listdir, remove
from sys import argv
from threading import Thread
from urllib.error import HTTPError

from bot.bot import Bot
from moviepy.editor import AudioFileClip
from pytube import YouTube
from youtubesearchpython import VideosSearch, CustomSearch

from addition.Constance import (ALLQUALITIES, EXCEPTIONS, PATTERN_FOR_CHOOSING,
                                PATTERN_FOR_SEARCH)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - " %(message)s "', datefmt='%H:%M:%S')


def run_in_thread(func):
    """ Running function in thread """

    def run(*args, **kwargs):
        proc = Thread(target=func, args=args if args else tuple(), kwargs=kwargs if kwargs else dict())
        return proc.start()

    return run


def install_youtube_video(url: str, res: str = None, audio: bool = False, path: str = None) \
        -> str:
    """ Install a YouTube video and give a path to it """
    if not audio:
        # Checking quality as others are not acceptable
        if res is None or res not in list(map(lambda x: int(x.strip('-')), ALLQUALITIES)):
            res = 360
        res = str(res) + 'p'

    # Downloading video
    for _ in range(3):
        try:
            if audio:
                video = YouTube(url=url).streams.filter(
                    subtype='mp4', type='audio').first()
            else:
                video = YouTube(url=url).streams.filter(
                    res=res, file_extension='mp4', progressive='True').first()
            if path:
                path = path.split('\\')
                video_path = video.download(
                    output_path='\\'.join(path[:-1]), filename=path[-1])
            else:
                video_path = video.download()

            # Convert to mp3 with thread
            if audio:
                video_path_list = list((None,))
                proc_ = Thread(target=mp4_to_mp3, args=(
                    video_path, video_path_list))
                proc_.start()
                proc_.join()
                video_path = video_path_list[-1]

            return video_path
        except ConnectionResetError as err:
            log(type(err), err, '-> Trying again!')
            continue
        except HTTPError as err:
            log(type(err), err, '-> Trying again!')
            continue
        except IOError as err:
            log(type(err), err)
            return 'Space'
        except Exception as err:
            log(type(err), err)
            return None
    else:
        return None


def mp4_to_mp3(path: str, return_list: list = None):
    log("Converting to mp3")
    video = AudioFileClip(path)
    video.write_audiofile(path.replace('mp4', 'mp3'), logger=None)
    os.remove(path)
    if return_list:
        return_list.append(path.replace('mp4', 'mp3'))
    return path.replace('mp4', 'mp3')


@run_in_thread
def print_bot(text: str, bot: Bot, user_id: str) -> None:
    """ Easier way to write sth to user """
    while True:
        try:
            sended_text_params = bot.send_text(
                chat_id=user_id, text=text, parse_mode='HTML')
        except Exception:
            continue
        else:
            return sended_text_params


@run_in_thread
def print_bot_button(bot, user_id: str = '705079793', text: str = 'Buttons:', url=False,
                     buttons: dict = None, in_row: int = 8, is_admin: bool = False, **kwargs):
    """ Print message to bot with buttons """
    if not buttons:
        buttons = kwargs
    keyboard = [[]]
    if isinstance(url, bool):
        action_type = "url" if url else "callbackData"

        for btn_text in buttons:
            if len(keyboard[-1]) >= in_row:
                keyboard.append([])
            if is_admin and not url:  # Admin addition
                buttons[btn_text] += ' -admin-'
                print(buttons[btn_text])

            keyboard[-1].append({"text": btn_text,
                                 action_type: buttons[btn_text]})
    elif hasattr(url, '__iter__'):
        if len(url) == len(buttons):
            for btn_text, is_url in zip(buttons, url):
                if len(keyboard[-1]) >= in_row:
                    keyboard.append([])
                if not is_url and is_admin:  # Admin addition
                    buttons[btn_text] = buttons[btn_text] + "-admin-"

                action_type = 'url' if is_url else "callbackData"
                keyboard[-1].append({"text": btn_text,
                                     action_type: buttons[btn_text]})
        else:
            raise IndexError(
                'buttons and url have different sizes, plz check them!')
    else:
        print_bot(text, bot, user_id)
        return False

    while True:
        try:
            bot.send_text(chat_id=user_id, text=text, parse_mode='HTML',
                          inline_keyboard_markup="{}".format(json.dumps(keyboard)))
        except BaseException:
            continue
        else:
            break
    return True


def log(*message, show: bool = True):
    if show:
        logging.warning(' '.join(map(str, message)))


def search_video_by_query(query: str, limit: int = 16, lang: str = 'en', is_admin: bool = False,
                          return_list: list = None, sort: object = None):
    """ Userfriendly interface, included google that search YouTube videos by query """
    if sort:
        results = CustomSearch(query, searchPreferences=sort, limit=limit, language=lang)
    else:
        results = VideosSearch(query, limit=limit, language=lang)
    num, text = 1, 'Results:'
    buttons = dict()

    for result in results.result()['result'][:16]:
        if 'playlist' in result['link']:
            continue
        text += PATTERN_FOR_SEARCH.format(num, result['title'], result['duration'],
                                          result['channel']['name'], result['publishedTime'])
        buttons[f'{num}'] = result['link'] + \
                            ' -admin-' if is_admin else result['link']
        num += 1

    if return_list:
        return_list.append(text)
        return_list.append(buttons)
    return text, buttons


def is_data_wrong(data: str) -> str:
    if data is None:
        return "Something went wrong, your message is not readable"
    elif 'https://www.google.com/url' in data:
        return "Please send https://youtu... link(not google link)"
    elif 'https://files.icq.net' in data:
        return "It is neither link nor query"
    elif 'playlist' in data:
        return "This is a playlist, please choose a video"
    else:
        return ''


def in_channel(bot, user_id: str, channel_id: str = "686692940@chat.agent"):
    """ Checking is a user on chat or not """
    try:
        lst_of_users = bot.get_chat_members(chat_id=channel_id).json()
        if 'cursor' in lst_of_users.keys():
            cur = '1221'
            while cur:
                cur = lst_of_users['cursor'] if 'cursor' in lst_of_users.keys(
                ) else None
                for user in lst_of_users['members']:
                    if user_id == user['userId']:
                        return True
                else:
                    lst_of_users = bot.get_chat_members(
                        chat_id=channel_id, cursor=cur).json()
            else:
                return False
        else:
            for user in lst_of_users['members']:
                if user_id == user['userId']:
                    return True
            else:
                return False
    except BaseException as err:
        log('Error in_channel: ', type(err), ':', err)
        return None


def links():
    """ Give 5 randomly choose videos that already exist in Google Drive """
    import googleapi

    # Preparing data
    lst_of_videos, lst_of_give = googleapi.get_all_files(), []
    if len(lst_of_videos) < 2:
        return 'No one download video since last clear', {'Google': 'google.com'}

    for video in lst_of_videos:  # Easy ways are not work
        if len(lst_of_give) >= 5:
            break
        elif video not in lst_of_give:
            lst_of_give.append(video)

    text, buttons = '', dict()

    for num, give in enumerate(lst_of_give):
        text += f"{num} -> {give['title']}\n\n"
        buttons[f' {num} '] = give['alternateLink']

    return text, buttons


def get_text_to_choose_quality(url: str):
    text = PATTERN_FOR_CHOOSING.format(url)
    buttons = dict()
    for quality in ALLQUALITIES + EXCEPTIONS:
        buttons[quality] = f"download:{url} {quality} -admin-" \
            if len(argv) > 1 else f"download:{url} {quality}"
    return text, buttons


@run_in_thread
def check_server_clearness():
    for file in listdir():
        if '.mp4' in file or '.mp3' in file:
            remove(file)


if __name__ == '__main__':
    log(input('log: '))
