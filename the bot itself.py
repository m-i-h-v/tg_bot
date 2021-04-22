from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler
from transform_scripts.color_transform import color_transformation
import os


def stop():
    return ConversationHandler.END


def start(update, context):
    update.message.reply_text('Привет, я бот-обработчик, можешь прислать мне фотографию и я её обработаю!')


def help(update, context):
    update.message.reply_text('Help message.')


def receive_photo(update, context):
    context.user_data['file_id'] = update.message.photo[-1].file_id
    update.message.reply_text('Я получил фото, какую обработку ты хочешь получить?')
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
    return ConversationHandler.END


def main():
    updater = Updater('1715854605:AAH3sMobHjmh9JImdAXTVlWTUy5yA-gWWQY', use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('start', start))

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.photo, receive_photo, pass_user_data=True)],
        states={
            1: [CommandHandler('b_w_transform', b_w_transform, pass_user_data=True)],
        },
        fallbacks=[CommandHandler('stop', stop),
                   MessageHandler(Filters.photo, receive_photo, pass_user_data=True)]
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()