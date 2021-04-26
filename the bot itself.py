from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CommandHandler, ConversationHandler
from transform_scripts.color_transform import color_transformation
from transform_scripts.palette_transform import palette_transformation
from transform_scripts.size_transform import size_transformation
from transform_scripts.invert_transform import invert_transformation
from transform_scripts.anaglyph_transform import anaglyph_transformation
from transform_scripts.supeimpose_transform import superimpose_transformation
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, \
    InlineKeyboardMarkup
import os


def start(update, context):
    update.message.reply_text('Привет, я бот-обработчик, можешь прислать '
                              'мне фотографию и я её обработаю!',
                              reply_markup=start_markup)
    return 1


def help(update, context):
    update.message.reply_text('Этот бот способен совершать некоторые опер'
                              'ации над изображениями, такие как: создание '
                              'чёрно-белой картинки, перевод изображение в '
                              'палитру определённых цветов, а также масштаби'
                              'рование изображения (с сохранением и без) отно'
                              'шения сторон. Умеет совмещать изображения и '
                              'создавать анаглифы! Бот умеет распознавать неко'
                              'торые сообщения, но для более удобно взаимо '
                              'действия рекомендуется использовать специальные'
                              ' кнопки, это ускорит общение с ботом. Если вы х'
                              'отите изменить фото, которое нужно обработать, '
                              'то можете просто отправить новое, бот обрабатыв'
                              'ает последнее полученное фото! При использовани'
                              'и масштабирования размер указывается в следующе'
                              'м порядке: ширина, высота.',
                              reply_markup=anaglyph_markup)


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
    for palette in range(1, 7):
        context.bot.send_photo(update.message.chat_id,
                               open(f'palette_images/palette_img_{palette}'
                                    f'.jpg', 'rb'))
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
    if len(nums) == 1 and 'любая' not in text.lower() and 0 < nums[0] < 7:
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
                                      f'прочитать о нём нажав на копку',
                                      reply_markup=nft_markup)
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
    elif 'совмест' in text.lower():
        update.message.reply_text('Хорошо, отправь мне изображение, которое ты'
                                  ' хочешь наложить',
                                  reply_markup=go_back_markup)
        return 7
    elif 'nft' in text.lower():
        update.message.reply_text(f'Хочешь узнать об NFT токенах и '
                                  f'продавать свои творения? Ты сможешь '
                                  f'прочитать о нём нажав на копку',
                                  reply_markup=nft_markup)
        return 1
    update.message.reply_text('Моя твоя не понимать')
    return 1


def variable_answer(update, context):
    text = update.message.text
    if 'да' in text.lower() or 'нет' in text.lower():
        context.user_data['save_ratio'] = 'да' in text.lower()
        update.message.reply_text('Выбери размер нового изображения '
                                  'или отправь свой',
                                  reply_markup=go_back_markup)
        return 5
    elif 'верн' in text.lower():
        update.message.reply_text('Какую обработку ты хочешь получить?',
                                  reply_markup=markup_receive_photo)
        return 1
    else:
        update.message.reply_text('Я не понял')
        return 4


def command_check(update, context):
    text = update.message.text
    if 'обработ' in text.lower():
        update.message.reply_text('Отправь мне фото и я её обработаю!')
        return 3
    elif 'нфт' in text.lower() or 'токен' in text.lower() \
            or 'nft' in text.lower() or 'token' in text.lower():
        update.message.reply_text(f'Хочешь узнать об NFT токенах и '
                                  f'продавать свои творения? Ты сможешь '
                                  f'прочитать о нём нажав на копку',
                                  reply_markup=nft_markup)
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
            update.message.reply_text('Ок')
            download_image(user_id, context)
            anaglyph_transformation(user_id, nums[0])
            update.message.reply_text('Держи',
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
        update.message.reply_text('Не понял тебя')
        return 6


def superimpose(update, context):
    text = update.message.text
    if text is not None:
        if 'верн' in text.lower():
            update.message.reply_text('Какую обработку ты хочешь получить?',
                                      reply_markup=markup_receive_photo)
            return 1
        else:
            update.message.reply_text('Я не понимаю')
            return 7
    context.user_data['file_id_'] = update.message.photo[-1].file_id
    update.message.reply_text('Выбери прозрачность первого изображени в процен'
                              'тах', reply_markup=go_back_markup)
    return 8


def transparency(update, context):
    user_id = update.message.from_user.id
    text = update.message.text
    nums = find_nums(text)
    if len(nums) == 1:
        if 0 <= nums[0] <= 100:
            download_image(user_id, context)
            file_id = context.user_data['file_id']
            context.user_data['file_id'] = context.user_data['file_id_']
            download_image(str(user_id) + '_', context)
            context.user_data['file_id'] = file_id
            superimpose_transformation(user_id, nums[0] / 100)
            update.message.reply_text('То что получилось:',
                                      reply_markup=markup_receive_photo)
            context.bot.send_photo(update.message.chat_id,
                                   open(f'user_images/{user_id}.jpg', 'rb'))
            os.remove(f'user_images/{user_id}.jpg')
            os.remove(f'user_images/{user_id}_.jpg')
            return 1
        else:
            update.message.reply_text('Прозрачность должна быть от 0 до 100')
            return 8
    if 'верн' in text.lower():
        update.message.reply_text('Какую обработку ты хочешь получить?',
                                  reply_markup=markup_receive_photo)
        return 1
    else:
        update.message.reply_text('Не понял тебя')
        return 8


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
            1: [CommandHandler('black_and_white', b_w_transform,
                               pass_user_data=True),
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
            6: [MessageHandler(Filters.text, anaglyph)],
            7: [MessageHandler(Filters.photo, superimpose,
                               pass_user_data=True),
                MessageHandler(Filters.text, superimpose,
                               pass_user_data=True)],
            8: [MessageHandler(Filters.text, transparency, pass_user_data=True)
                ]},
        fallbacks=[MessageHandler(Filters.photo, receive_photo,
                                  pass_user_data=True)]
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    reply_keyboard = [['Хочу чёрно-белую', 'Переведи в палитру цветов',
                       'Масштабируй изображение'],
                      ['Инвертируй цвета', 'Сделай анаглиф',
                       'Совмести изображения'],
                      ['Что ты умеешь?', 'Что такое NFT токен?']]
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
    btn = InlineKeyboardButton('Что такое анаглиф?',
                               url='https://ru.wikipedia.org/wiki/%D0%90%D0%BD'
                                   '%D0%B0%D0%B3%D0%BB%D0%B8%D1%84')
    anaglyph_markup = InlineKeyboardMarkup([[btn]])
    btn = InlineKeyboardButton('Что такое NFT токен?',
                               url='https://ru.wikipedia.org/wiki/%D0%9D%D0%B5'
                                   '%D0%B2%D0%B7%D0%B0%D0%B8%D0%BC%D0%BE%D0%B7'
                                   '%D0%B0%D0%BC%D0%B5%D0%BD%D1%8F%D0%B5%D0%BC'
                                   '%D1%8B%D0%B9_%D1%82%D0%BE%D0%BA%D0%B5%D0%B'
                                   'D')
    nft_markup = InlineKeyboardMarkup([[btn]])
    main()
