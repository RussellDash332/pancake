import os, platform, requests, time
from bs4 import BeautifulSoup
from zipfile import ZipFile
from urllib.request import urlretrieve
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from pancake import Pancake, DeluxePancake

HTML_FN = 'run.html'

version = requests.get('https://chromedriver.storage.googleapis.com/LATEST_RELEASE').text
curr_os = platform.platform()

def download_chromedriver():
    try: os.remove('chromedriver.zip')
    except: pass
    print('Downloading "chromedriver.exe"...')
    url = f'https://chromedriver.storage.googleapis.com/{version}/chromedriver_win32.zip'
    urlretrieve(url, 'chromedriver.zip')
    with ZipFile('chromedriver.zip') as chromezip:
        chromezip.extractall()
    os.remove('chromedriver.zip')

def start_browser(mode=None):
    if mode == None:
        mode = int(input('Daily Waffle or Deluxe Waffle? (1 or 2)\n'))
        assert mode in [1, 2], 'Invalid mode selected'
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    browser = webdriver.Chrome(options=options)
    browser.maximize_window()
    browser.set_page_load_timeout(30)
    try:
        browser.get('https://wafflegame.net/')
        print('Closing how-to popup...')
        browser.find_element(By.XPATH, '/html/body/div[6]/div/header/button[2]').click()
        print('Fake-solving to enable timezone change...')
        while int(browser.find_element(By.CLASS_NAME, 'swaps__val').text) > 0:
            elements = list(browser.find_elements(By.CLASS_NAME, 'draggable:not(.green)'))
            ActionChains(browser).drag_and_drop(elements[0], elements[1]).perform()
        print('Clicking menu button...')
        browser.find_element(By.CLASS_NAME, 'button--menu.icon-button').click()

        wait = WebDriverWait(browser, 5)
        print('Opening settings...')
        wait.until(expected_conditions.element_to_be_clickable((By.CLASS_NAME, 'button--settings.icon-button'))).click()
        print('Switching to local time...')
        wait.until(expected_conditions.element_to_be_clickable((By.CLASS_NAME, 'switch-tab:not(.switch-tab__selected)'))).click()
        print('Loading new Waffle...')
        wait.until(expected_conditions.element_to_be_clickable((By.XPATH, '/html/body/div[7]/div/header/button[2]'))).click()

        if mode == 2:
            time.sleep(5)
            print('Clicking menu button...')
            wait.until(expected_conditions.element_to_be_clickable((By.CLASS_NAME, 'button--menu.icon-button'))).click()
            print('Opening Deluxe Waffle...')
            wait.until(expected_conditions.element_to_be_clickable((By.CLASS_NAME, 'button--deluxe.icon-button'))).click()
        time.sleep(5)
    except:
        browser.quit()
        return start_browser(mode)
    html_doc = browser.page_source
    browser.quit()
    #open(HTML_FN, 'wb+').write(html_doc.encode())
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
    if size == 5:   Pancake(board=new_board, verdict=new_verdict).solve()
    elif size == 7: DeluxePancake(board=new_board, verdict=new_verdict).solve()
    else:           print(f'Ignoring invalid size of {size}...')

if __name__ == '__main__':
    if curr_os.startswith('Windows'):
        print('Getting HTML source page...')
        try:
            soup = start_browser()
        except Exception as e:
            print('Issue found:', e)
            download_chromedriver()
            soup = start_browser()
        print('Done! Parsing source page now...\n')
        parse(soup)
        print()
    while True:
        try:
            print(input(f'Paste the whole page source at {HTML_FN}, and press Enter when you\'re done:\n'))
            html_doc = ''.join(map(bytes.decode, open(HTML_FN, 'rb').readlines()))
            parse(BeautifulSoup(html_doc, 'html.parser'))
            print()
        except KeyboardInterrupt: break
        except Exception as e:
            print('HTML page source cannot be parsed :( Skipping!')
            print('Issue:', e)
