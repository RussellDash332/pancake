# Telebot integration
from main import *

Pancake.IS_TELEGRAM = True
try:    TOKEN, CHATS = os.environ['TOKEN'], os.environ['CHAT'].split(',')
except: from env import TOKEN, CHATS

def send(token, chat_id, bot_message):
    resp = requests.get(f'https://api.telegram.org/bot{token}/sendMessage', params={
        'chat_id': chat_id,
        'parse_mode': 'MarkdownV2',
        'text': bot_message,
        'disable_web_page_preview': True
        })
    logging.info(resp.json())

curr_os = (pf:=platform.platform())[:pf.find('-')]
supplier = {'Windows': get_windows_browser, 'Linux': get_linux_browser}.get(curr_os)
assert supplier, f'Pancake not supported for {curr_os} yet :('

bot_message = parse(loop_resolve(start_browser, handle_chromedriver, 5, get_mode(), supplier))
for chat_id in CHATS.split(','): send(TOKEN, chat_id, bot_message)
