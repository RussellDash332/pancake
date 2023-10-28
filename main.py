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
from urllib.request import urlretrieve
from webdriver_manager.chrome import ChromeDriverManager
from zipfile import ZipFile

logging.basicConfig(
    level=logging.INFO, 
    format= '[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

with open('version.txt', 'r') as f:
    __VERSION__ = f.readline().split()[1]

def get_mode():
    if len(sys.argv) == 1:  mode = int(input('Daily Waffle or Deluxe Waffle? (1 or 2)\n'))
    else:                   mode = int(sys.argv[1])
    assert mode in [1, 2], 'Invalid mode selected'
    return mode

def loop_resolve(f, resolution, lim, *args):
    if lim == 0:
        raise Exception('Reached the limit for number of tries')
    try:
        return f(*args)
    except Exception as e:
        print('Issue found:', e)
        resolution()
        return loop_resolve(f, resolution, lim-1, *args)

def download_chromedriver():
    version = __VERSION__ #requests.get('https://chromedriver.storage.googleapis.com/LATEST_RELEASE').text
    try: os.remove('chromedriver.zip')
    except: pass
    logging.info('Downloading "chromedriver.exe"...')
    url = f'https://chromedriver.storage.googleapis.com/{version}/chromedriver_win32.zip'
    urlretrieve(url, 'chromedriver.zip')
    with ZipFile('chromedriver.zip') as chromezip:
        chromezip.extractall()
    os.remove('chromedriver.zip')

def get_windows_browser():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless') # to debug, comment this line
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    browser = webdriver.Chrome(options=options)
    return browser

def get_linux_browser():
    version = __VERSION__ #requests.get('https://chromedriver.storage.googleapis.com/LATEST_RELEASE').text
    chrome_service = Service(ChromeDriverManager(chrome_type='chromium', driver_version=version).install())
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
    if size == 5:   return Pancake(board=new_board, verdict=new_verdict).solve()
    elif size == 7: return DeluxePancake(board=new_board, verdict=new_verdict).solve()
    else:           print(f'Ignoring invalid size of {size}...')

def handle_chromedriver():
    curr_os = (pf:=platform.platform())[:pf.find('-')]
    if curr_os == 'Windows': download_chromedriver()

if __name__ == '__main__':
    curr_os = (pf:=platform.platform())[:pf.find('-')]
    supplier = {'Windows': get_windows_browser, 'Linux': get_linux_browser}.get(curr_os)
    assert supplier, f'Pancake not supported for {curr_os} yet :('

    mode = get_mode()
    soup = loop_resolve(start_browser, handle_chromedriver, 5, mode, supplier)
    logging.info('Source page obtained! Parsing source page now...\n')
    parse(soup)
    input('Press enter to quit...')
