import os, platform, requests
from bs4 import BeautifulSoup
from zipfile import ZipFile
from urllib.request import urlretrieve
from selenium import webdriver
from pancake import Pancake, DeluxePancake

version = requests.get('https://chromedriver.storage.googleapis.com/LATEST_RELEASE').text
curr_os = platform.platform()

def download_chromedriver():
    print('Downloading "chromedriver.exe"...')
    url = f'https://chromedriver.storage.googleapis.com/{version}/chromedriver_win32.zip'
    urlretrieve(url, 'chromedriver.zip')
    with ZipFile('chromedriver.zip') as chromezip:
        chromezip.extractall()
    os.remove('chromedriver.zip')

def start_browser():
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    browser = webdriver.Chrome(options=options)
    browser.minimize_window()
    browser.set_page_load_timeout(30)
    try:
        browser.get('https://wafflegame.net/')
    except:
        browser.close()
        return start_browser()
    return BeautifulSoup(browser.page_source, 'html.parser')

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
            board[(x, y)], verdict[(x, y)] = div.text, v
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
        except:
            download_chromedriver()
            soup = start_browser()
        print('Done! Parsing source page now...\n')
        parse(soup)
        print()
    while True:
        try:
            print(input('Paste the whole page source at run.html, and press Enter when you\'re done:\n'))
            html_doc = ''.join(map(bytes.decode, open('run.html', 'rb').readlines()))
            parse(BeautifulSoup(html_doc, 'html.parser'))
            print()
        except KeyboardInterrupt: break
        except Exception as e:
            print('HTML page source cannot be parsed :( Skipping!')
            print('Issue:', e)