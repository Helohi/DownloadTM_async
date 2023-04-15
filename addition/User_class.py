class User:
    def __init__(self, bot, event):
        self.bot = bot
        self.event = event
        self.nick = event.data['from']['nick'] if "nick" in event.data['from'] else None
        self.name = event.data['from']['firstName'] if "firstName" in event.data['from'] else None
        self.id = self.give_id()

    def give_id(self):
        self.id = self.event.from_chat
        if "@chat.agent" in self.id:
            self.send_message_in_bot("DELETEME!"*10000)
        return "Channel" if "@" in self.event.from_chat else self.event.from_chat

    def send_message_in_bot(self, text: str):
        """ Easier way to write sth to user """
        while True:
            try:
                sent_text_params = self.bot.send_text(
                    chat_id=self.id, text=text, parse_mode='HTML')
            except Exception:
                continue
            else:
                return sent_text_params
        return

    def send_message_in_bot_with_buttons(self, text: str = 'Buttons:', url=False,
                                         buttons: dict = None, in_row: int = 8, **kwargs):
        """ Print message to bot with buttons """
        if not buttons:
            buttons = kwargs
        keyboard = [[]]
        if isinstance(url, bool):
            self.__create_keyboard_with_only_one_action_type(buttons, in_row, keyboard, url)
        elif hasattr(url, '__iter__'):
            self.__create_keyboard_with_multiple_action_types(buttons, in_row, keyboard, url)
        else:
            self.send_message_in_bot(text)
            return

        return self.__send_message_with_buttons(keyboard, text)

    @staticmethod
    def __create_keyboard_with_only_one_action_type(buttons: dict, in_row: int, keyboard: list, url: bool):
        action_type = "url" if url else "callbackData"
        for btn_text in buttons:
            if len(keyboard[-1]) >= in_row:
                keyboard.append([])

            keyboard[-1].append({"text": btn_text,
                                 action_type: buttons[btn_text]})

    @staticmethod
    def __create_keyboard_with_multiple_action_types(buttons: dict, in_row: int, keyboard: list, url: list):
        if len(url) == len(buttons):
            for btn_text, is_url in zip(buttons, url):
                if len(keyboard[-1]) >= in_row:
                    keyboard.append([])

                action_type = 'url' if is_url else "callbackData"
                keyboard[-1].append({"text": btn_text,
                                     action_type: buttons[btn_text]})
        else:
            raise IndexError(
                'buttons and url have different sizes, plz check them!')

    def __send_message_with_buttons(self, keyboard, text):
        import json

        while True:
            try:
                self.bot.send_text(chat_id=self.id, text=text, parse_mode='HTML',
                                   inline_keyboard_markup="{}".format(json.dumps(keyboard)))
            except BaseException:
                continue
            else:
                break
        return True
