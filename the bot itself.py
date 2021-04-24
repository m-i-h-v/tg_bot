from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler
from transform_scripts.color_transform import color_transformation
from transform_scripts.palette_transform import palette_transformation
from telegram import ReplyKeyboardMarkup
import os


LINKS = {'nft': 'тут ссылка'}


def stop():
    return ConversationHandler.END


def start(update, context):
    update.message.reply_text('Привет, я бот-обработчик, можешь прислать мне фотографию и я её обработаю!')
    return 1


def help(update, context):
    update.message.reply_text('Help message.')


def receive_photo(update, context):
    context.user_data['file_id'] = update.message.photo[-1].file_id
    update.message.reply_text('Я получил фото, какую обработку ты хочешь получить?',
                              reply_markup=markup)
    return 1


def b_w_transform(update, context):
    user_id = update.message.from_user.id
    if os.path.exists(f'user_images/{user_id}.jpg'):
        os.remove(f'user_images/{user_id}.jpg')
    file_id = context.user_data['file_id']
    file = context.bot.getFile(file_id)
    file.download(f'user_images/{user_id}.jpg')
    color_transformation(f'user_images/{user_id}.jpg')
    context.bot.send_photo(update.message.chat_id, open(f'user_images/{user_id}.jpg', 'rb'))
    os.remove(f'user_images/{user_id}.jpg')
    return 1


def palette_chosen(update, context):
    update.message.reply_text('Выбери палитру цветов')
    for palette in range(1, 3):
        context.bot.send_photo(update.message.chat_id, open(f'palettes/palette_{palette}.jpg', 'rb'))
    return 2


def palette_transform(update, context):
    text = update.message.text
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
    if len(nums) == 1 and 'любая' not in text.lower() and 0 < nums[0] < 3:
        user_id = update.message.from_user.id
        if os.path.exists(f'user_images/{user_id}.jpg'):
            os.remove(f'user_images/{user_id}.jpg')
        file_id = context.user_data['file_id']
        file = context.bot.getFile(file_id)
        file.download(f'user_images/{user_id}.jpg')
        palette_transformation(f'user_images/{user_id}.jpg', nums[0])
        context.bot.send_photo(update.message.chat_id, open(f'user_images/{user_id}.jpg', 'rb'))
        os.remove(f'user_images/{user_id}.jpg')
        update.message.reply_text('Держи')
        return 1
    else:
        data = phrase_check(update, context)
        if data is None:
            if 'nft' or 'token' or 'нфт' or 'токен' in text.lower():
                update.message.reply_text(f'Хочешь узнать об NFT токенах и продавать свои творения? Ты сможешь почитать о нём здесь: {LINKS["nft"]}')
            else:
                update.message.reply_text('Я тебя не понял')
                update.message.reply_text('Используй быстрые команды, это удобно и легко')
            return 2
        else:
            return data

def phrase_check(update, context):
    text = update.message.text
    if 'черн' in text.lower() or 'бел' in text.lower() or 'чёрн' in text.lower():
        update.message.reply_text('Отличный выбор, сейчас сделаю в ч/б')
        b_w_transform(update, context)
        return 1
    elif 'палитр' in text.lower() or 'набор' in text.lower():
        palette_chosen(update, context)
        return 2
    update.message.reply_text('Моя твоя не понимать')
    return 1


def command_check(update, context):
    text = update.message.text
    if 'обработ' in text.lower():
        update.message.reply_text('Отправь мне фото и я её обработаю!')
        return 3
    elif 'нфт' in text.lower() or 'токен' in text.lower() \
            or 'nft' in text.lower() or 'token' in text.lower():
        update.message.reply_text(f'Хочешь узнать об NFT токенах и продавать свои творения? Ты сможешь почитать о нём здесь: {LINKS["nft"]}')
        return 3
    else:
        update.message.reply_text('Я тебя не понял')
        update.message.reply_text('Ты можешь воспользоваться кнопками быстрых комманд, это легко и удобно!')
        return 3


def simple_reply(update, context):
    update.message.reply_text('Для начала пришли мне фото')
    return 3


def main():
    updater = Updater('1715854605:AAH3sMobHjmh9JImdAXTVlWTUy5yA-gWWQY', use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('start', start))

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.photo, receive_photo, pass_user_data=True),
                      MessageHandler(Filters.text, command_check, pass_user_data=True)],
        states={
            1: [CommandHandler('b_w_transform', b_w_transform, pass_user_data=True),
                CommandHandler('palette_chosen', palette_chosen, pass_user_data=True),
                MessageHandler(Filters.text, phrase_check, pass_user_data=True)],
            2: [MessageHandler(Filters.text, palette_transform, pass_user_data=True)],
            3: [MessageHandler(Filters.photo, receive_photo, pass_user_data=True),
                CommandHandler('b_w_transform', simple_reply),
                CommandHandler('palette_chosen', simple_reply)]
        },
        fallbacks=[MessageHandler(Filters.photo, receive_photo, pass_user_data=True)]
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    reply_keyboard = [['/b_w_transform', '/palette_chosen']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    main()