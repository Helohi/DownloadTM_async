import addition.functions as func
from bot.bot import Bot, Event
from addition.User_class import User
from addition.UserMessage_class import UserMessage
import addition.Constance as Text


class UserButtons(User):
    def __init__(self, bot: Bot, event: Event):
        super().__init__(bot, event)
        self.callback_query = event.callback_query
        self.stop_user_button_from_loading()

        func.log(f"Got button callbak from: id={self.id}, name={self.name}, nick={self.nick}, "
                 f"callquery={self.callback_query}")

    def stop_user_button_from_loading(self):
        self.bot.answer_callback_query(
            query_id=self.event.data['queryId'],
            text="Got it!",
            show_alert=False
        )

    @func.run_in_thread
    def work_out(self):
        if 'delete:' in self.callback_query:
            self.delete_file_from_google_drive()
        elif 'download:' in self.callback_query:  # Check spammness and send to UserMessage
            self.download_video_via_UserMessage_class()
        else:  # Ask to choose quality
            self.__ask_user_to_choose_quality()

    def delete_file_from_google_drive(self):
        import addition.googleapi as gapi

        gapi.delete_one_file(file_name=self.callback_query.lstrip('delete:'))
        self.send_message_in_bot("<b>Thank you</b> for saving memory!👍❤")

    def download_video_via_UserMessage_class(self):
        if UserMessage.is_user_processing(self):  # No Spam
            func.log(f"Spamming id={self.id}")
            self.send_message_in_bot(Text.NO_SPAM)
        else:
            self.callback_query = self.callback_query.lstrip("download:")
            self.change_into_UserMessage()

    def change_into_UserMessage(self):
        self.event.text = self.callback_query
        downloading = UserMessage(self.bot, self.event).check_all_conditions_and_work_out()
        del downloading
        return

    def __ask_user_to_choose_quality(self):
        text, buttons = func.get_text_to_choose_quality(self.callback_query)
        return self.send_message_in_bot_with_buttons(text, buttons=buttons, in_row=3)
