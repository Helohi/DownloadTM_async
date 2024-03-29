import logging
import os
from os import listdir, remove
from sys import argv
from threading import Thread
from urllib.error import HTTPError
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


def log(*message, show: bool = True):
    if show:
        logging.warning(' '.join(map(str, message)))


def search_video_by_query(query: str, limit: int = 16, lang: str = 'en', is_admin: bool = False, sort: object = None):
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
