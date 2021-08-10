import telebot, random


def web_ring_gen(message, channel_link, config):
    try:
        channel_list = open('ring_list', 'r').read().splitlines()
    except FileNotFoundError:
        open('ring_list', 'w').close()
        channel_list = open('ring_list', 'r').read().splitlines()
    if message.chat.type == "private":
        channel_link = message.text
    else:
        channel_link = 'https://t.me/' + message.chat.username
    try:
        current_channel_pos = channel_list.index(channel_link)
        if current_channel_pos == len(channel_list) - 1:
            next_channel = channel_list[0].replace('https://t.me/', '@')
            previous_channel = channel_list[current_channel_pos - 1].replace('https://t.me/', '@')
        elif current_channel_pos == 0:
            next_channel = channel_list[current_channel_pos + 1].replace('https://t.me/', '@')
            previous_channel = channel_list[-1].replace('https://t.me/', '@')
        else:
            next_channel = channel_list[current_channel_pos + 1].replace('https://t.me/', '@')
            previous_channel = channel_list[current_channel_pos - 1].replace('https://t.me/', '@')
        random_channel = channel_list[random.randint(0, len(channel_list) - 1)].replace('https://t.me/', '@')
        list_channels = config['ChannelList']['link']
        return next_channel, previous_channel, random_channel, list_channels
    except ValueError:
        print(channel_link, 'not in list')
        return None, None, None, None