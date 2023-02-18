TOKEN = "001.3036675131.1370245590:1007918545"
TOKEN_admin = "001.4089497866.3095557866:1008754555"
ALLQUALITIES = ['-360-', '-720-']
EXCEPTIONS = ['-audio-']
CHANNELLINK = '\nCheckout new updates on " https://icq.im/TM_team "'
HELP = "Hello new user! I'm here to introduce myself:\n"\
        "First of all subscribe to channel ' https://icq.im/TM_team '\n"\
        "To Search: Just write something. Example: <i>' Mario song '</i>\n"\
        "Then choose video and download it with some quality (not all qualities will work)\n"\
        "To download: Write link with quality. Example: "\
        "<i>'https://www.youtube.com/watch?v=icPHcK_cCF4 -360-'</i>\n"\
        f"All possible quality ({', '.join(ALLQUALITIES)})\n"\
        f"More functions: {', '.join(EXCEPTIONS)}\n"\
        "You can also write ' /links '\n"\
        "/queue will help you figure out how many people in queue\n"\
        "----- Русский -----\n"\
        "Привет, новый пользователь! Я покажу как мною пользоваться:\n"\
        "Сначала подпишись на этот канал ' https://icq.im/TM_team '\n"\
        "Что бы искать просто напиши в боте свой вопрос. Например: 'Толстой Война и мир'\n"\
        "После выбери любое видео, а потом и качество (Не все качества будут работать)\n"\
        "Что бы просто скачать видео вставь ссылку на видео, а рядом качество. Например: "\
        "<i>'https://www.youtube.com/watch?v=icPHcK_cCF4 -360-'</i>\n"\
        f"Все возможные качества: {', '.join(ALLQUALITIES)}\n"\
        f"Ещё функции: {', '.join(EXCEPTIONS)}\n"\
        "Не знаешь что посмотреть? Попробуй ' /links '\n"\
        "/queue - Поможет узнать количество людей в очереди"
NO_VIDEO_QUALITY = "Bot can\'t find this video with given <b>quality</b>.\n"\
                 "Check your video length, more than 1 hour may cause problem.\n" \
                 "Try again with <i>another quality</i>! ' <b>/help</b> ' \n"\
                 "---------Русский---------\n"\
                 "Бот не может найти это видео в данном качестве\n"\
                 "Проверьте длинну вашего видео, больше 1 часа может вызвать проблемы у бота\n" \
                 "Попробуйте выбрать <i>другое качество</i>! или ' <b>/help</b> '"
PAY = "Now the bot works only by subscription, its cost is small. To buy: @musicstar\n" \
      "-----------Русский-----------\n" \
      "Теперь бот работает только по подписке, стоимость ее небольшая. Для покупки: @musicstar"
NO_SPAM = "We already got your requests! Please wait till we process it\n-----------\nМы уже получили от вас запрос! " \
         "Просим подождать пока мы его не обра<b>бот</b>аем"
PATTERN_FOR_CHOOSING = "url: {}\nChoose quality:"
PATTERN_FOR_SEARCH = """\n\n{}. NAME: <i>{}</i>
DURATION: <b>{}</b>
FROM: <i>{}</i>
WHEN: <b>{}</b>\n\n"""
ERROR_OCCURE = "Bot🤖 got an error 🤦‍♂️, users list📃 was removed.\nPlease send📩 your reqests again🔁!\n" \
              "---------- Русский ----------\nБот🤖 получил ошибку 🤦‍♂️, лист📃 с пользователями был удален\n" \
              "Пожалуйста повторите🔁 свое последнее действие/запрос📩!"
TIME_RROR = "Your request take too long to be done, maybe your video is too long, if not please try again or write " \
            "to @tm_team.\n----Rusian---\nВаш запрос обрабатывется слишком долго, возможно ваше видео слишком " \
            "большое.\nЕсли нет пожалуйста попробуйте заново или напишите @tm_team."
MAX_TIME = 900