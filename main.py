import configparser
import telebot, random
import telebot as tb
from widget import web_ring_gen


def update_config():
    config.read('config.ini')
    return config


config = configparser.ConfigParser()
config = update_config()
tb_token = config['TelegramBot']['token']
bot = tb.TeleBot(tb_token)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if str(message.from_user.id) in [admin_id.strip() for admin_id in config['AdminPanel']['ids'].split(',')]:
        bot.send_message(message.from_user.id, """
Welcome to *Yet Another Telegram Web Ring Bot*!
Use /admin_help to to get administrative information""", parse_mode='Markdown')


@bot.message_handler(commands=['add'])
def channel_add(message):
    if str(message.from_user.id) in [admin_id.strip() for admin_id in config['AdminPanel']['ids'].split(',')]:
        bot.send_message(message.from_user.id, 'Send me the channel, which you want to add.',
                         disable_web_page_preview=True)
        bot.register_next_step_handler(message, channel_add_handler)


def channel_add_handler(message):
    try:
        channel_list = open('ring_list', 'r').read().splitlines()
    except FileNotFoundError:
        open('ring_list', 'w').close()
        channel_list = open('ring_list', 'r').read().splitlines()
    if message.text not in channel_list:
        bot_status = channel_checking_system(message)
        if bot_status:
            channel_list.append(message.text.lower())
            channel_list.sort()
            ring_add_file = open('ring_list', 'w')
            ring_add_file.write('\n'.join(channel_list))
            ring_add_file.close()
            description_changer(message)
            update_ring_list()
            bot.send_message(message.from_user.id, 'Channel successfully added.')
    else:
        bot.send_message(message.from_user.id, 'Channel is already in list')


@bot.message_handler(commands=['remove'])
def channel_delete(message):
    if str(message.from_user.id) in [admin_id.strip() for admin_id in config['AdminPanel']['ids'].split(',')]:
        bot.send_message(message.from_user.id, 'Send me the channel, which you want to delete.',
                         disable_web_page_preview=True)
        bot.register_next_step_handler(message, channel_delete_handler)


def channel_delete_handler(message):
    try:
        channel_list = open('ring_list', 'r').read().splitlines()
    except FileNotFoundError:
        open('ring_list', 'w').close()
        channel_list = open('ring_list', 'r').read().splitlines()
    if message.text in channel_list:
        channel_list.remove(message.text)
        open('ring_list', 'w').writelines(channel_list)
        bot.leave_chat(message.text.replace('https://t.me/', '@'))
        bot.send_message(message.from_user.id, 'Channel deleted from list')
    else:
        bot.send_message(message.from_user.id, 'Channel in not in list')


@bot.message_handler(commands=['list'])
def widget_activating(message):
    if str(message.from_user.id) in [admin_id.strip() for admin_id in config['AdminPanel']['ids'].split(',')]:
        try:
            channel_list = open('ring_list', 'r').read().splitlines()
            bot.send_message(message.from_user.id, 'Ring List Channels:\n' + '\n'.join(channel_list),
                             disable_web_page_preview=True)
        except FileNotFoundError:
            bot.send_message(message.from_user.id, 'Ring List is empty',
                             disable_web_page_preview=True)


def channel_checking_system(message):
    channel_link = message.text.replace('https://t.me/', '@')
    channel_info = bot.get_chat(channel_link)
    try:
        activating_message = bot.send_message(channel_link,
                                              'Bot Ring Activating',
                                              disable_notification=True)
        bot.delete_message(channel_link, activating_message.id)
        web_ring_name = config['WebRing']['text']
        if config['WebRing']['text'] in channel_info.description:
            description = channel_info.description.split(config['WebRing']['text'])[0].strip()
        else:
            description = channel_info.description
        if len(description) > 100 + len(web_ring_name):
            bot.send_message(message.from_user.id, 'Description is too long. Web ring need some more characters: *' +
                             str(len(description) - (100 + len(web_ring_name))) + '*', parse_mode='Markdown')
            return False
        return True
    except telebot.apihelper.ApiException as telebot_error:
        if telebot_error.result.status_code == 403:
            bot.send_message(message.from_user.id, 'Bot is not a member of the channel.')
        elif telebot_error.result.status_code == 400:
            bot.send_message(message.from_user.id, 'Link incorrect or bot does not have enough permissions.')
        else:
            print(telebot_error.result.content)
        return False


@bot.channel_post_handler(content_types=['text', 'photo'])
def channel_widget_bot(message):
    description_changer(message)


def description_changer(message):
    if message.chat.type == "private":
        channel_link = message.text.replace('https://t.me/', '@')
    else:
        channel_link = '@' + message.chat.username
    channel_description = bot.get_chat(channel_link).description
    if config['WebRing']['text'] in channel_description:
        description = channel_description.split(config['WebRing']['text'])[0].strip()
    else:
        description = channel_description

    next_channel, previous_channel, random_channel, list_channels = web_ring_gen(message, channel_link)
    try:
        bot.set_chat_description(channel_link, description + '\n' + config['WebRing']['text'] +
f'''
Next: {next_channel}
Previous: {previous_channel}
Random: {random_channel}
List: {list_channels}''')
    except telebot.apihelper.ApiException as description_change_error:
        if description_change_error.result.status_code == 400:
            return
        else:
            print('description_error', description_change_error)


def update_ring_list():
    channel_list = open('ring_list', 'r').read().splitlines()
    current_list = bot.send_message(config['ChannelList']['link'],
                                    '\n'.join(channel_list),
                                    disable_notification=True,
                                    disable_web_page_preview=True,
                                    )
    for id_list in range(int(current_list.id) - 3, int(current_list.id)):
        try:
            bot.delete_message(config['ChannelList']['link'], id_list)
        except telebot.apihelper.ApiTelegramException:
            pass


bot.polling(none_stop=True)
