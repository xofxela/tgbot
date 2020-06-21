# -*- coding: utf-8 -*-
import telebot
import config
import os
import re
from PIL import Image
import requests
import shutil
# Global
bot = telebot.TeleBot(config.TOKEN)
language_code = 'ru'
chat_name = 'SOGIS'
bot_name = f'{bot.get_me().username}'
sticker_pack_name = f'{chat_name}_by_{bot_name}'
bot_id = bot.get_me().id
user_id = None

@bot.message_handler(commands=['start'])
def welcome_msg(message):
    bot.send_chat_action(message.chat.id, 'typing')
    global language_code
    language_code = message.from_user.language_code
    if language_code == 'ru':
        bot.send_message(message.chat.id, f'Привет, {str(message.from_user.first_name)}, меня зовут  {bot_name}\nЖми /help и увидишь, что я умею', parse_mode='html')
    else:
        bot.send_message(message.chat.id, f'Hello, {str(message.from_user.first_name)}, my name is {bot_name}\nPress /help to see what i can', parse_mode='html')

@bot.message_handler(commands=['help'])
def help_msg(message):
    bot.send_chat_action(message.chat.id, 'typing')
    if language_code == 'ru':
        bot.send_message(message.chat.id, f'Я умею:\n\n'+\
    f'Добавлять/удалять фото или стикер в https://t.me/addstickers/{sticker_pack_name}\nДля этого есть кнопки ➕ или ➖. Кнопка 🚫 отменяет действие\n\n'+\
    f'Создавать новый набор стикеров. При отправке фото введи название набора и затем нажми кнопку 🆕\n', parse_mode='html')
    else:
        bot.send_message(message.chat.id, f'I can:\n\n'+\
    f'Add/remove photo or sticker to https://t.me/addstickers/{sticker_pack_name}\nUse ➕ or ➖. The 🚫 button cancells operation\n\n'+\
    f'Create new sticker set. While you attach photo, enter title and then press 🆕 button', parse_mode='html')

@bot.message_handler(content_types=['text'])
def text_util(message):
    bot.send_chat_action(message.chat.id, 'typing')
    if language_code == 'ru':
        bot.send_message(message.chat.id, 'Жми /help и увидишь, что я умею')
    else:
        bot.send_message(message.chat.id, 'Press /help to see what i can')

@bot.message_handler(content_types=['photo'])
def photo_util(message):
    global user_id
    user_id = message.from_user.id
    bot.send_chat_action(message.chat.id, 'typing')
    try:

            kb = telebot.types.InlineKeyboardMarkup(row_width=2)
            if message.caption:
                but1 = telebot.types.InlineKeyboardButton('🆕', callback_data='create')
            else:
                but1 = telebot.types.InlineKeyboardButton('➕', callback_data='add_photo')
            but2 = telebot.types.InlineKeyboardButton('🚫', callback_data='cancel')
            kb.add(but1, but2)
            bot.send_photo(message.chat.id, message.photo[0].file_id, caption=message.caption, reply_markup=kb)
    except Exception as e:
        print(e)

@bot.message_handler(content_types=['sticker'])
def sticker_util(message):
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        kb = telebot.types.InlineKeyboardMarkup(row_width=3)
        but1 = telebot.types.InlineKeyboardButton('➕', callback_data='add_sticker')
        but2 = telebot.types.InlineKeyboardButton('➖', callback_data='remove_sticker')
        but3 = telebot.types.InlineKeyboardButton('🚫', callback_data='cancel')
        kb.add(but1, but2, but3)
        bot.send_sticker(message.chat.id, message.sticker.file_id, reply_markup=kb)
    except Exception as e:
        print(e)

@bot.callback_query_handler(lambda call: True)
def iq_callback(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_chat_action(call.message.chat.id, 'typing')
    try:
        if call.message:
            if call.data == 'add_photo':
                add_photo(call.message)
            elif call.data == 'create':
                create_pack(call.message, call.message.caption)
            elif call.data == 'add_sticker':
                add_sticker(call.message)
            elif call.data == 'remove_sticker':
                remove_sticker(call.message)
            elif call.data == 'cancel':
                if language_code == 'ru':
                    bot.send_message(call.message.chat.id, 'Отменено')
                else:
                    bot.send_message(call.message.chat.id, 'Cancelled')
            else:
                if language_code == 'ru':
                    bot.send_message(call.message.chat.id, 'Нажми /help')
                else:
                    bot.send_message(call.message.chat.id, 'Press /help')
    except Exception as e:
        print(e)

def create_pack(message, title):
    try:
        if re.search('[a-zA-Z]', title[0]) and 1<=len(title)<=64 and re.search('^[a-zA-Z0-9_]*$', title) and not re.search('^[__]*$', title):
            img_file_path = bot.get_file(message.photo[0].file_id)
            url = f'https://api.telegram.org/file/bot{config.TOKEN}/{img_file_path.file_path}'
            img = Image.open(requests.get(url, stream=True).raw)
            if img.width > img.height:
                basewidth = 512
                wpercent = (basewidth/float(img.size[0]))
                hsize = int((float(img.size[1])*float(wpercent)))
                img = img.resize((basewidth,hsize))
            else:
                baseheight = 512
                wpercent = (baseheight/float(img.size[1]))
                wsize = int((float(img.size[0])*float(wpercent)))
                img = img.resize((wsize, baseheight))
            img.save('temp.png', 'png')
            if language_code == 'ru':
                if bot.create_new_sticker_set(user_id=f'{str(user_id)}', name=f'{title}_by_{bot_name}', title=f'{title}', png_sticker=open('temp.png', 'rb'), emojis='💬'):
                    bot.send_message(message.chat.id, f'Пак создан: https://t.me/addstickers/{title}_by_{bot_name}')
                else:
                    bot.send_message(message.chat.id, f'Пак с названием {title} уже создан, используй другое название', parse_mode='html')
            else:
                if bot.create_new_sticker_set(user_id=f'{str(user_id)}', name=f'{title}_by_{bot_name}', title=f'{title}', png_sticker=open('temp.png', 'rb'), emojis='💬'):
                    bot.send_message(message.chat.id, f'Pack created: https://t.me/addstickers/{title}_by_{bot_name}')
                else:
                    bot.send_message(message.chat.id, f'Pack with title {title} already exists, use another title', parse_mode='html')
            # Delete temp files
            img.close()
            os.remove('temp.png', dir_fd=None)
        else:
            if language_code == 'ru':
                bot.send_message(message.chat.id, 'Название в пределах 1-64 символа и начинается с латинской буквы')
            else:
                bot.send_message(message.chat.id, 'Title must contain 1-64 symbols and start with latin letter')
    except Exception as e:
        print(e)

def add_sticker(message):
    try:
        # Get file_path, send GET request to API, open .webp file from response data, convert it and save as .png
        img_file_path = bot.get_file(message.sticker.file_id)
        url = f'https://api.telegram.org/file/bot{config.TOKEN}/{img_file_path.file_path}'
        img = Image.open(requests.get(url, stream=True).raw)
        img.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=255)
        alpha = img.split()[-1]
        mask = Image.eval(alpha, lambda a: 255 if a <=128 else 0)
        img.paste(255, mask)
        img.save('temp.png', 'png')
        # Add to sticker pack
        if bot.add_sticker_to_set(user_id = bot_id, name = f'{sticker_pack_name}', png_sticker = open('temp.png', 'rb'), emojis = message.sticker.emoji):
            if language_code == 'ru':
                bot.send_message(message.chat.id, f'Стикер добавлен в\nhttps://t.me/addstickers/{sticker_pack_name}', reply_markup=None, parse_mode='html')
            else:
                bot.send_message(message.chat.id, f'Sticker has been added to\nhttps://t.me/addstickers/{sticker_pack_name}', reply_markup=None, parse_mode='html')
        # Delete temp files
        img.close()
        os.remove('temp.png', dir_fd=None)
    except Exception as e:
        print(e)
        if language_code == 'ru':
            bot.send_message(message.chat.id, 'Ошибка добавления стикера, попробуй снова')
        else:
            bot.send_message(message.chat.id, 'Add sticker error, try again')

def remove_sticker(message):
    try:
        # Remove from sticker pack
        stickerset = bot.get_sticker_set(message.sticker.set_name)
        if bot.delete_sticker_from_set(message.sticker.file_id):
            if language_code == 'ru':
                bot.send_message(message.chat.id, f'Стикер удален из\nhttps://t.me/addstickers/{sticker_pack_name}', reply_markup=None, parse_mode='html')
            else:
                bot.send_message(message.chat.id, f'Sticker has been removed from\nhttps://t.me/addstickers/{sticker_pack_name}', reply_markup=None, parse_mode='html')
    except Exception as e:
        print(e)
        if language_code == 'ru':
            bot.send_message(message.chat.id, f'Такого стикера нет в наборе\nhttps://t.me/addstickers/{sticker_pack_name}')
        else:
            bot.send_message(message.chat.id, f'There is no such sticker in\nhttps://t.me/addstickers/{sticker_pack_name}')

def add_photo(message):
    try:
        img_file_path = bot.get_file(message.photo[0].file_id)
        url = f'https://api.telegram.org/file/bot{config.TOKEN}/{img_file_path.file_path}'
        img = Image.open(requests.get(url, stream=True).raw)
        if img.width > img.height:
            basewidth = 512
            wpercent = (basewidth/float(img.size[0]))
            hsize = int((float(img.size[1])*float(wpercent)))
            img = img.resize((basewidth,hsize))
        else:
            baseheight = 512
            wpercent = (baseheight/float(img.size[1]))
            wsize = int((float(img.size[0])*float(wpercent)))
            img = img.resize((wsize, baseheight))
        img.save('temp.png', 'png')
        # Add to sticker pack
        if bot.add_sticker_to_set(user_id = bot_id, name = f'{sticker_pack_name}', png_sticker = open('temp.png', 'rb'), emojis = '💬'):
            if language_code == 'ru':
                bot.send_message(message.chat.id, f'Стикер добавлен в\nhttps://t.me/addstickers/{sticker_pack_name}', reply_markup=None, parse_mode='html')
            else:
                bot.send_message(message.chat.id, f'Sticker has been added to\nhttps://t.me/addstickers/{sticker_pack_name}', reply_markup=None, parse_mode='html')
        # Delete temp files
        img.close()
        os.remove('temp.png', dir_fd=None)
    except Exception as e:
        print(e)
        if language_code == 'ru':
            bot.send_message(message.chat.id, 'Ошибка добавления стикера, попробуй снова')
        else:
            bot.send_message(message.chat.id, 'Add sticker error, try again')
# RUN
if __name__ == '__main__':
    bot.infinity_polling()