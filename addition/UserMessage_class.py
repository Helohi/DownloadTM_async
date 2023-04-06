from bot.bot import Bot, Event
import os
from addition.User_class import User
import addition.functions as func
import addition.Constance as Text
from addition import googleapi


class UserMessage(User):
    processing = dict()

    def __init__(self, bot: Bot, event: Event):
        super().__init__(bot, event)
        self.text = event.text.strip() if event.text is not None else event.msgId
        func.log(f"Get text:  id={self.id}, name={self.name}, nick={self.name}. Query={self.text}")
        self.check_all_conditions_and_work_out()

    @func.run_in_thread
    def check_all_conditions_and_work_out(self):
        if self.text == '/start' or self.text == '/help':  # Start
            self.answer_to_basic_commands()
        elif self.is_user_processing():  # No Spamming
            func.log(f"Spamming id={self.id}")
            self.send_message_in_bot(Text.NO_SPAM)
        elif self.is_subscribed() is False:  # Not suscribed
            self.send_message_in_bot(Text.PAY)
        elif message_to_send := func.is_data_wrong(self.text):  # Error in data
            self.send_message_in_bot(message_to_send)
        else:  # All checks passed correctly
            UserMessage.processing[self.id] = self.event
            self.work_out()

    def answer_to_basic_commands(self):
        if self.text == '/start' or self.text == '/help':
            self.send_message_in_bot(Text.HELP)

    def is_user_processing(self):
        if self.id in UserMessage.processing:
            return True
        return False

    def is_subscribed(self, channel_id: str = "686692940@chat.agent"):
        """ Checking wether user subscribed on channel or not """
        try:
            subscibers = self.bot.get_chat_members(chat_id=channel_id).json()
            if 'cursor' in subscibers.keys():
                return self.__checker_for_large_channel(channel_id, subscibers)
            else:
                return self.__checker_for_small_channels(subscibers)
        except BaseException as err:
            func.log('Error in_channel: ', type(err), ':', err)
            return None

    def __checker_for_large_channel(self, channel_id: str, lst_of_users: list):
        cur = True
        while cur:
            cur = lst_of_users['cursor'] if 'cursor' in lst_of_users.keys() else None
            for user in lst_of_users['members']:
                if self.id == user['userId']:
                    return True
            else:
                lst_of_users = self.bot.get_chat_members(
                    chat_id=channel_id, cursor=cur).json()
        else:
            return False

    def __checker_for_small_channels(self, lst_of_users):
        for user in lst_of_users['members']:
            if self.id == user['userId']:
                return True
        else:
            return False

    def delete_user_from_processing(self):
        if self.id in self.processing:
            del self.processing[self.id]

    def work_out(self):
        """ It contains all algorithms, that download video """
        # If Links (put it here becouse it use a lot of resources)
        try:
            if self.text == '/links':
                self.__find_and_send_text_for_link()

            elif "youtube" in self.text or "youtu.be" in self.text:
                self.__install_youtube_video()

            else:  # To not spam Channels
                self.search_video_by_query()
        except BaseException as err:
            func.log(f"Error:{type(err)}, {err}")
            self.send_message_in_bot(f"Ошибка какая-то, отправьте ее админу, он поможет\n{type(err)}: {err}")
        finally:
            # Finishing with user
            self.delete_user_from_processing()
            googleapi.check_drive()

    def __find_and_send_text_for_link(self):
        text, buttons = self.__make_text_wich_answer_to_link()  # (text to send, buttons)
        return self.send_message_in_bot_with_buttons(text=text, url=True, buttons=buttons)

    @staticmethod
    def __make_text_wich_answer_to_link():
        """ Give 5 randomly choose videos that already exist in Google Drive """
        import random

        # Preparing data
        lst_of_videos = googleapi.get_all_files()
        if len(lst_of_videos) < 2:
            return 'No one download video since last clear', {'Google': 'google.com'}
        lst_of_give = [random.choice(lst_of_videos) for _ in range(5)]
        text, buttons = '', dict()

        for num, give in enumerate(lst_of_give):
            text += f"{num} -> {give['title']}\n\n"
            buttons[f' {num} '] = give['alternateLink']

        return text, buttons

    def __install_youtube_video(self):
        import re

        # Preparing data
        if opt := re.findall("-[0-9]{3,4}-", self.text):  # If user give us a quality
            opt = int(opt[0].replace('-', ''))
        elif '-audio-' in self.text:
            opt = 'audio'
        else:
            opt = ''

        url = self.text.replace(f'-{opt}-', '').strip()
        if not opt:  # Need quality
            return self.__ask_user_to_choose_quality()

        func.log(f'start working {self.id}, {self.name}')
        func.log(f"Downloading video to server")
        self.send_message_in_bot(text=f'URL:<i>{url}</i>\nWith quality:<b>{opt}</b>\nStart downloading...')

        if opt == 'audio':
            path = func.install_youtube_video(url=url, audio=True)
        else:
            path = func.install_youtube_video(url=url, res=opt)

        if path is None:  # No such video quality
            self.send_message_in_bot(Text.NO_VIDEO_QUALITY)
            return
        elif path == 'Space':  # No space on server
            self.send_message_in_bot('Not enough space on server, please try later!')
            self.bot.send_text(text='Clear me!', chat_id='705079793')
            return

        self._send_video(path)

    def __ask_user_to_choose_quality(self):
        text, buttons = func.get_text_to_choose_quality(self.text)
        return self.send_message_in_bot_with_buttons(text=text, buttons=buttons, in_row=3)

    def _send_video(self, path):
        """ Function for sending video """
        func.log(f"In function -> sending video")
        if os.path.getsize(path) > 40_000_000:  # By Google Drive
            self.__send_video_via_google_drive(path)
        else:  # by ICQ
            self.__send_video_via_icq(path)

    def __send_video_via_google_drive(self, path):
        import addition.googleapi as gapi

        func.log("Sending by google drive")
        try:
            link = gapi.upload_file(path=path, title=os.path.basename(path))
        except BaseException as err:
            self.send_message_in_bot('Error with <i>google drive</i>, pls try again <b>later</b>')
            func.log('Error with Google Drive:', type(err), err)
        else:
            self.send_message_in_bot_with_buttons(text=f'I did it! Link:\n{link} ', url=[
                True, False], Link=link, Delete=f"delete:{os.path.basename(path)}")
        finally:
            self.delete_file_from_server(path)

    def __send_video_via_icq(self, path):
        func.log("Sending by icq")
        for _ in range(3):
            try:
                with open(path, 'rb') as file:
                    sended_file = self.bot.send_file(
                        chat_id=self.id, file=file)
                    if sended_file.status_code != 200:
                        continue
            except BaseException as err:
                print(type(err), ':', err)
                self.__send_video_via_google_drive(path)
                break
            else:
                self.delete_file_from_server(path)
                break
        else:
            self.__send_video_via_google_drive(path)

    def search_video_by_query(self):
        self.send_message_in_bot(
            text=f'I\'m searching <b>{self.text}</b> on youtube:')
        lang = self.__get_lang_in_message()
        sort = self.__get_sort_in_message()
        try:
            text, buttons = func.search_video_by_query(query=self.text, lang=lang, sort=sort)
            if not buttons:
                self.send_message_in_bot(text='No results found')
            else:
                self.send_message_in_bot_with_buttons(text=text, buttons=buttons)
        except BaseException as err:
            self.send_message_in_bot('Error with <i>Google search</i>, pls try <b>later</b>')
            func.log('Error with Google search', type(err), err)

    def __get_lang_in_message(self):
        lang = 'en'
        for char in ['-ru-', '-en-']:
            if char in self.text:
                lang = char.strip('-')
        return lang

    def __get_sort_in_message(self):
        from youtubesearchpython import VideoSortOrder
        sort = None
        if "-rate-" in self.text:
            sort = VideoSortOrder.rating
        elif "-view-" in self.text:
            sort = VideoSortOrder.viewCount
        elif "-date-" in self.text:
            sort = VideoSortOrder.uploadDate
        elif "-rel-" in self.text:
            sort = VideoSortOrder.relevance
        return sort

    @staticmethod
    def delete_file_from_server(path):
        func.log("Removing file from server")
        os.remove(path)
