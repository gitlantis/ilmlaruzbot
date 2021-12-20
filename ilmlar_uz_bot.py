import time, json, os, telebot, string, html
from telebot import types

from ilmlar import Ilmlar

TOKEN = ''

constants = {}
knownUsers = [] 
userStep = {}  
userSearch = {}  
search = about = ''
mainButtons = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)  

hideButtons = types.ReplyKeyboardRemove()

if __name__ == "__main__":
    
    with open('{}/constants.json'.format(os.path.dirname(__file__)), encoding="utf8") as f:
        constants = json.load(f)

    search = constants['search']
    about = constants['about']    
    TOKEN = constants['token']  
    mainButtons.add(search, about)
    
    
def get_user_step(uid):
    
    if uid in userStep:
        return userStep[uid]
    else:
        knownUsers.append(uid)
        # about and help
        return 0


def listener(messages):
    for m in messages:
        if m.content_type == 'text':
            # print the sent message to the console
            print(str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " + m.text)

bot = telebot.TeleBot(TOKEN)
bot.set_update_listener(listener)  # register listener

@bot.message_handler(commands=['start'])
def command_start(m):
    cid = m.chat.id

    ilmlar = Ilmlar()

    ilmlar.add_user(cid)

    if cid not in knownUsers:  
        command_about(m)
        command_help(m)
    else:
        command_help(m)

@bot.message_handler(commands=['help'])
def command_help(m):
    cid = m.chat.id
    help_text = "<b>Buyruqlar:</b> \n"
    for key in constants['commands']: 
        help_text += key + " : "
        help_text += constants['commands'][key] + "\n"
    bot.send_message(cid, help_text, reply_markup=mainButtons, parse_mode='HTML') 
    userStep[cid] = 0

@bot.message_handler(commands=['statistics'])
def command_start(m):
    
    cid = m.chat.id

    ilmlar = Ilmlar()

    if cid in [1093604775,2143076098,76384044]:
        count = ilmlar.count_user()
        bot.send_message(cid, "foydalanuvchilar: {}".format(count), reply_markup=hideButtons) 
    else:
        search(m)

@bot.message_handler(func=lambda message: message.text == constants['about'] or message.text == '/about')
def command_about(m):
    cid = m.chat.id

    about_text = constants['about_text']

    bot.send_photo(chat_id=cid, photo=open("{}{}".format(os.path.dirname(__file__),constants['desc_image']), 'rb'), caption=about_text, reply_markup=mainButtons, parse_mode='HTML')
    userStep[cid] = 0
    
@bot.message_handler(func=lambda message: message.text == constants['search'])
def command_image(m):
    cid = m.chat.id
    bot.send_message(cid, "So'zni kiriting", reply_markup=hideButtons) 
    userStep[cid] = 1  

@bot.inline_handler(func=lambda message: len(message.query) > 0)
def command_image(m):
    inline_search(m)


@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 1)
def msg_image_select(m):
    search(m)   

@bot.callback_query_handler(func=lambda query: query.data.startswith('/backward'))
def command_start(m):
    text = m.data   
    page = int(text.split()[1])
    #if page>0:
    search(m.message, int(page), True)
    
@bot.callback_query_handler(func=lambda query: query.data.startswith('/forward'))
def command_start(m):
    text = m.data
    page = text.split()[1]

    search(m.message, int(page), True)
    
@bot.message_handler(func=lambda message: True, content_types=['text'])
def command_default(m):
    cid = m.chat.id
    text = m.text

    if text!=search or text!=about:
        userStep[cid] = 0
        search(m)
        #bot.send_message(m.chat.id, 'Saytdan qidirish uchun "{}" tugmasini bosing'.format(constants['search']), reply_markup=mainButtons)
    else:
        bot.send_message(m.chat.id, "Kerakli so'zni kiriting", reply_markup=mainButtons)       

def search(m, page=1, edit=False):
    cid = m.chat.id
    text = m.text    

    bot.send_chat_action(cid, 'typing')
    ilmlar = Ilmlar()
    ilmlar.add_search(text)
    
    try: 
        if edit:
            if page<1 :
                bot.edit_message_text(chat_id=m.chat.id, message_id=m.id, text=constants['end_of_search'], reply_markup=navigator(page), disable_web_page_preview=True, parse_mode='HTML')            
            else:
                result = ilmlar.search(userSearch[cid], page)
                if len(result)!=0:
                    bot.edit_message_text(chat_id=m.chat.id, message_id=m.id, text=result, reply_markup=navigator(page), disable_web_page_preview=True, parse_mode='HTML')
                else:
                    bot.edit_message_text(chat_id=m.chat.id, message_id=m.id, text=constants['end_of_search'], reply_markup=navigator(page), disable_web_page_preview=True, parse_mode='HTML')
                    
                    #bot.send_message(m.chat.id, constants['end_of_search'], reply_markup=mainButtons, disable_web_page_preview=True)
                    
        else:
            userSearch[cid] = text
            result = ilmlar.search(text, page)
            
            bot.send_message(m.chat.id, result, reply_markup=navigator(page), disable_web_page_preview=True, parse_mode='HTML')
            bot.send_message(m.chat.id, constants['magnifier'], reply_markup=mainButtons, disable_web_page_preview=True)
        
        userStep[cid] = 0         
        
    except Exception as e:
        print(str(e))
        bot.send_message(m.chat.id, constants['not_found'], reply_markup=mainButtons, disable_web_page_preview=True)
        userStep[cid] = 1 

def inline_search(m):
    try:
        result = []         
        ilmlar = Ilmlar()        
        res = ilmlar.inline_search(m.query)
        i=0
        for key,value in res.items():
           r = types.InlineQueryResultArticle(str(i), html.unescape(key), types.InputTextMessageContent(value)) 
           result.append(r)
           i+=1
        
        if len(result)>0:
            bot.answer_inline_query(m.id, result)
            
    except Exception as e:
        print(e)


def navigator(page):
    button = types.InlineKeyboardMarkup()
    # back = types.InlineKeyboardButton(constants['back'], callback_data='/backward {}'.format(str(page-1)))
    # forw = types.InlineKeyboardButton(constants['forward'], callback_data='/forward {}'.format(str(page+1)))
    site = types.InlineKeyboardButton(constants['web_title'], url=constants['web_site'])
    #search = types.InlineKeyboardButton(constants['search'], callback_data='/search')
    #button.row(back, forw)
    button.row(site)
    #button.row(search)
    return button

bot.infinity_polling()
