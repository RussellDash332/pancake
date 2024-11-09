import argparse
import logging
import os
import platform
import requests
import sys
import time
from bs4 import BeautifulSoup
from pancake import Pancake, DeluxePancake
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

logging.basicConfig(
    level=logging.INFO, 
    format= '[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

def loop_resolve(f, resolution, lim, *args):
    if lim == 0:
        raise Exception('Reached the limit for number of tries')
    try:
        return f(*args)
    except Exception as e:
        print('Issue found:', e)
        resolution()
        return loop_resolve(f, resolution, lim-1, *args)

def get_windows_browser():
    service = Service()
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    browser = webdriver.Chrome(service=service, options=options)
    return browser

def get_linux_browser():
    chrome_service = Service(ChromeDriverManager(chrome_type='chromium').install())
    chrome_options = Options()
    options = [
        "--headless",
        "--disable-gpu",
        "--window-size=1920,1200",
        "--ignore-certificate-errors",
        "--disable-extensions",
        "--no-sandbox",
        "--disable-dev-shm-usage"
    ]
    for option in options: chrome_options.add_argument(option)
    browser = webdriver.Chrome(service=chrome_service, options=chrome_options)
    browser.execute_cdp_cmd('Emulation.setTimezoneOverride', {'timezoneId': 'Singapore'})
    return browser

def start_browser(mode, supplier):
    browser = supplier()
    browser.maximize_window()
    browser.set_page_load_timeout(30)
    try:
        logging.info('Getting HTML source page...')
        browser.get('https://wafflegame.net/' + ['daily', 'deluxe'][mode-1])
        logging.info('Switching to local time...')
        browser.execute_script('''localStorage.setItem('settings', '{"highcontrast":false,"darkmode":false,"localTimezoneEnabled":true}')''')
        logging.info('Refreshing page...')
        browser.refresh()
        time.sleep(5)
    except:
        browser.quit()
        return start_browser(mode, supplier)
    html_doc = browser.page_source
    browser.quit()
    return BeautifulSoup(html_doc, 'html.parser')

def parse(soup):
    board, verdict = {}, {}
    for div in soup.find_all('div', class_='tile'):
        classes = div.get('class')
        if 'draggable' in classes:
            xy = eval(div.get('data-pos'))
            x, y = xy['x'], xy['y']
            if 'yellow' in classes: v = 'Y'
            elif 'green' in classes: v = 'G'
            else: v = '-'
            board[(y, x)], verdict[(y, x)] = div.text, v
    size = max(board)[0] + 1
    new_board, new_verdict = [], []
    for i in range(size):
        for j in range(size):
            if (i, j) in board:
                new_board.append(board[(i, j)].lower())
                new_verdict.append(verdict[(i, j)].upper())
    new_board, new_verdict = map(''.join, [new_board, new_verdict])
    return new_board, new_verdict, size

def solve(board, verdict, size):
    if size == 5:   return Pancake(board=board, verdict=verdict).solve()
    elif size == 7: return DeluxePancake(board=board, verdict=verdict).solve()
    else:           print(f'Ignoring invalid size of {size}...')

def run():
    curr_os = (pf:=platform.platform())[:pf.find('-')]
    supplier = {'Windows': get_windows_browser, 'Linux': get_linux_browser}.get(curr_os)
    assert supplier, f'Pancake not supported for {curr_os} yet :('

    parser = argparse.ArgumentParser(prog='pancake', description='Solve Waffle in no time')
    parser.add_argument('-m', '--mode', help='Waffle mode (1 for daily, 2 for deluxe)')
    parser.add_argument('-c', '--cron', default=0, help='Delay solving until new day (0 or 1)')
    args = parser.parse_args()

    if int(args.cron):
        while (t:=int(time.time()%86400))//3600 < 16: # not 4PM GMT yet
            time.sleep(10)
            logging.info(f'Waiting... Current time: {str(t//3600).zfill(2)}:{str(t//60%60).zfill(2)}:{str(t%60).zfill(2)} GMT')

    soup = loop_resolve(start_browser, lambda: None, 5, int(args.mode), supplier)
    logging.info('Source page obtained! Parsing source page now...\n')
    board, verdict, size = parse(soup)
    return solve(board, verdict, size)

if __name__ == '__main__':
    run()