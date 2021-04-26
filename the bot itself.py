from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CommandHandler, ConversationHandler
from transform_scripts.color_transform import color_transformation
from transform_scripts.palette_transform import palette_transformation
from transform_scripts.size_transform import size_transformation
from transform_scripts.invert_transform import invert_transformation
from transform_scripts.anaglyph_transform import anaglyph_transformation
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import os


LINKS = {'nft': 'тут ссылка'}


def stop():
    return ConversationHandler.END


def start(update, context):
    update.message.reply_text('Привет, я бот-обработчик, можешь прислать '
                              'мне фотографию и я её обработаю!',
                              reply_markup=start_markup)
    return 1


def help(update, context):
    update.message.reply_text('Этот бот способен совершать не которые опер'
                              'ации над изображениями, такие как: создание '
                              'чёрно-белой картинки, перевод изображение в '
                              'палитру определённых цветов, а также масштаби'
                              'рование изображения (с сохранением и без) отно'
                              'шения сторон Бот умеет распознавать некоторые '
                              'сообщения, но для более удобно взаимодействия '
                              'рекомендуется использовать специальные кнопки, '
                              'это ускорит общение с ботом. Если вы хотите '
                              'изменить фото, которое нужно обработать, то '
                              'можете просто отправить новое, бот обрабатывает'
                              ' последнее полученное фото! При использовании '
                              'масштабирования размер указывается в следующем '
                              'порядке: ширина, высота.')


def receive_photo(update, context):
    context.user_data['file_id'] = update.message.photo[-1].file_id
    update.message.reply_text('Я получил фото, какую обработку '
                              'ты хочешь получить?',
                              reply_markup=markup_receive_photo)
    return 1


def b_w_transform(update, context):
    user_id = update.message.from_user.id
    download_image(user_id, context)
    color_transformation(f'user_images/{user_id}.jpg')
    context.bot.send_photo(update.message.chat_id,
                           open(f'user_images/{user_id}.jpg', 'rb'))
    os.remove(f'user_images/{user_id}.jpg')
    return 1


def palette_chosen(update, context):
    update.message.reply_text('Выбери палитру цветов',
                              reply_markup=markup_choose_palette)
    for palette in range(1, 3):
        context.bot.send_photo(update.message.chat_id,
                               open(f'palettes/palette_{palette}.jpg', 'rb'))
    return 2


def find_nums(text):
    nums, num, digit = [], '', False
    for i in text:
        if i.isdigit():
            if not digit:
                digit = True
            num += i
        elif digit:
            digit = False
            nums.append(int(num))
            num = ''
    if num != '':
        nums.append(int(num))
    return nums


def download_image(user_id, context):
    if os.path.exists(f'user_images/{user_id}.jpg'):
        os.remove(f'user_images/{user_id}.jpg')
    file_id = context.user_data['file_id']
    file = context.bot.getFile(file_id)
    file.download(f'user_images/{user_id}.jpg')


def palette_transform(update, context):
    text = update.message.text
    nums = find_nums(text)
    if len(nums) == 1 and 'любая' not in text.lower() and 0 < nums[0] < 3:
        update.message.reply_text('Понял, сделаю в течении минуты',
                                  reply_markup=markup_receive_photo)
        user_id = update.message.from_user.id
        download_image(user_id, context)
        palette_transformation(f'user_images/{user_id}.jpg', nums[0])
        update.message.reply_text('Держи')
        context.bot.send_photo(update.message.chat_id,
                               open(f'user_images/{user_id}.jpg', 'rb'))
        os.remove(f'user_images/{user_id}.jpg')

        return 1
    else:
        if 'nft' in text.lower() or 'token' in text.lower() \
                or 'нфт' in text.lower() or 'токен' in text.lower():
            update.message.reply_text(f'Хочешь узнать об NFT токенах и '
                                      f'продавать свои творения? Ты сможешь '
                                      f'почитать о нём здесь: {LINKS["nft"]}')
            return 2
        elif 'верн' in text.lower():
            update.message.reply_text('Какую обработку ты хочешь получить?',
                                      reply_markup=markup_receive_photo)
            return 1
        else:
            update.message.reply_text('Такой палитры у меня нет, '
                                      'но ты можешь выбрать из имеющихся)')
            return 2


def phrase_check(update, context):
    text = update.message.text
    if 'черн' in text.lower() or 'бел' in text.lower() \
            or 'чёрн' in text.lower():
        update.message.reply_text('Отличный выбор')
        b_w_transform(update, context)
        return 1
    elif 'палитр' in text.lower() or 'набор' in text.lower():
        palette_chosen(update, context)
        return 2
    elif 'инверт' in text.lower():
        user_id = update.message.from_user.id
        update.message.reply_text('Инвертирую цвета...')
        download_image(user_id, context)
        invert_transformation(user_id)
        context.bot.send_photo(update.message.chat_id,
                               open(f'user_images/{user_id}.jpg', 'rb'))
        os.remove(f'user_images/{user_id}.jpg')
        update.message.reply_text('Here you are')
        return 1
    elif 'масштаб' in text.lower():
        update.message.reply_text('Ты хочешь сохранить соотношение сторон?',
                                  reply_markup=variable_question_markup)
        return 4
    elif 'верн' in text.lower():
        update.message.reply_text('Какую обработку ты хочешь получить?',
                                  reply_markup=markup_receive_photo)
        return 1
    elif 'анаглиф' in text.lower():
        update.message.reply_text('Хорошо, выбери смещение для изображения',
                                  reply_markup=go_back_markup)
        return 6
    elif 'умеешь' in text.lower():
        help(update, context)
        return 1
    update.message.reply_text('Моя твоя не понимать')
    return 1


def variable_answer(update, context):
    text = update.message.text
    if 'да' in text.lower() or 'нет' in text.lower():
        context.user_data['save_ratio'] = 'да' in text.lower()
        update.message.reply_text('Выбери размер нового изображения '
                                  'или отправь свой',
                                  reply_markup=ReplyKeyboardRemove())
        return 5
    else:
        num = phrase_check(update, context)
        return num


def command_check(update, context):
    text = update.message.text
    if 'обработ' in text.lower():
        update.message.reply_text('Отправь мне фото и я её обработаю!')
        return 3
    elif 'нфт' in text.lower() or 'токен' in text.lower() \
            or 'nft' in text.lower() or 'token' in text.lower():
        update.message.reply_text(f'Хочешь узнать об NFT токенах и продавать '
                                  f'свои творения? Ты сможешь почитать о '
                                  f'нём здесь: {LINKS["nft"]}')
        return 3
    elif 'умеешь' in text.lower():
        help(update, context)
        return 3
    else:
        update.message.reply_text('Я тебя не понял')
        update.message.reply_text('Ты можешь воспользоваться кнопками '
                                  'быстрых комманд, это легко и удобно!')
        return 3


def resize(update, context):
    text = update.message.text
    nums = find_nums(text)
    user_id = update.message.from_user.id
    download_image(user_id, context)
    if 0 < len(nums) < 3:
        size_transformation(user_id, context.user_data['save_ratio'], *nums)
        update.message.reply_text('А вот и оно!',
                                  reply_markup=markup_receive_photo)
        context.bot.send_photo(update.message.chat_id,
                               open(f'user_images/{user_id}.jpg', 'rb'))
        os.remove(f'user_images/{user_id}.jpg')
        return 1
    elif 'верн' in text.lower():
        update.message.reply_text('Какую обработку ты хочешь получить?',
                                  reply_markup=markup_receive_photo)
        return 1
    else:
        update.message.reply_text('Это не похоже на размер изображения!!!')
        return 5


def anaglyph(update, context):
    text = update.message.text
    user_id = update.message.from_user.id
    nums = find_nums(text)
    if len(nums) == 1:
        if nums[0] == 0:
            update.message.reply_text('Смещение изображения должно '
                                      'быть больше 0')
            return 6
        else:
            update.message.replyt_text('Ок')
            download_image(user_id, context)
            anaglyph_transformation(user_id, nums[0])
            update.message.reply_text('Держи',
                                      reply_markup=markup_receive_photo)
            context.bot.send_photo(update.message.chat_id,
                                   open(f'user_images/{user_id}.jpg'), 'rb')
            os.remove(f'user_images/{user_id}.jpg')
            return 1
    elif 'верн' in text.lower():
        update.message.reply_text('Какую обработку ты хочешь получить?',
                                  reply_markup=markup_receive_photo)
        return 1
    else:
        update.message.reply_text('Не понял тебя')
        return 6


def simple_reply(update, context):
    update.message.reply_text('Для начала пришли мне фото')
    return 3


def main():
    updater = Updater('1715854605:AAH3sMobHjmh9JImdAXTVlWTUy5yA-gWWQY',
                      use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('start', start))

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.photo, receive_photo,
                                     pass_user_data=True),
                      MessageHandler(Filters.text, command_check,
                                     pass_user_data=True)],
        states={
            1: [CommandHandler('b_w', b_w_transform, pass_user_data=True),
                CommandHandler('palette', palette_chosen, pass_user_data=True),
                MessageHandler(Filters.text, phrase_check)],
            2: [MessageHandler(Filters.text, palette_transform,
                               pass_user_data=True)],
            3: [MessageHandler(Filters.photo, receive_photo,
                               pass_user_data=True),
                CommandHandler('b_w', simple_reply),
                CommandHandler('palette', simple_reply),
                MessageHandler(Filters.text, command_check)],
            4: [MessageHandler(Filters.text, variable_answer,
                               pass_user_data=True)],
            5: [MessageHandler(Filters.text, resize, pass_user_data=True)],
            6: [MessageHandler(Filters.text, anaglyph)]
        },
        fallbacks=[MessageHandler(Filters.photo, receive_photo,
                                  pass_user_data=True)]
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    reply_keyboard = [['Хочу чёрно-белую', 'Переведи в палитру цветов',
                       'Масштабируй изображение', 'Инвертируй цвета',
                       'Сделай анаглиф'], ['Что ты умеешь?']]
    markup_receive_photo = ReplyKeyboardMarkup(reply_keyboard,
                                               one_time_keyboard=False,
                                               resize_keyboard=True)
    reply_keyboard = [['1', '2', '3'], ['4', '5', '6'], ['Вернуться']]
    markup_choose_palette = ReplyKeyboardMarkup(reply_keyboard,
                                                one_time_keyboard=False,
                                                resize_keyboard=True)
    reply_keyboard = [['Обработай мне фото', 'Что ты умеешь?']]
    start_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False,
                                       resize_keyboard=True)
    reply_keyboard = [['Да', 'Нет'], ['Вернуться']]
    variable_question_markup = ReplyKeyboardMarkup(reply_keyboard,
                                                   one_time_keyboard=False,
                                                   resize_keyboard=True)
    reply_keyboard = [['Вернуться']]
    go_back_markup = ReplyKeyboardMarkup(reply_keyboard,
                                         one_time_keyboard=False,
                                         resize_keyboard=True)
    main()