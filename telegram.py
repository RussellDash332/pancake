# Telebot integration
from main import *

Pancake.IS_TELEGRAM = True
try:    TOKEN, CHATS = os.environ['TOKEN'], os.environ['CHATS']
except: from env import TOKEN, CHATS

def send(token, chat_id, bot_message):
    resp = requests.get(f'https://api.telegram.org/bot{token}/sendMessage', params={
        'chat_id': chat_id,
        'parse_mode': 'MarkdownV2',
        'text': bot_message,
        'disable_web_page_preview': True
        })
    logging.info(resp.ok)

bot_message = run()
for chat_id in CHATS.split(','): send(TOKEN, chat_id, bot_message)
