import os, time, sys
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from pancake import Pancake, DeluxePancake

chrome_service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())

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
for option in options:
    chrome_options.add_argument(option)

def start_browser(mode=None):
    if mode == None:
        mode = int(sys.argv[1])
    browser = webdriver.Chrome(service=chrome_service, options=chrome_options)
    browser.maximize_window()
    browser.set_page_load_timeout(30)
    try:
        print('Getting HTML source page...')
        browser.get('https://wafflegame.net/')
        print('Closing how-to popup...')
        browser.find_element(By.XPATH, '/html/body/div[6]/div/header/button[2]').click()
        print('Fake-solving to enable timezone change...')
        while int(browser.find_element(By.CLASS_NAME, 'swaps__val').text) > 0:
            elements = list(browser.find_elements(By.CLASS_NAME, 'draggable:not(.green)'))
            src = elements[0]
            dst = None
            for i in range(1, len(elements)):
                if src.text != elements[i].text:
                    dst = elements[i]
                    break
            assert dst != None, 'electric boogaloo'
            ActionChains(browser).drag_and_drop(src, dst).perform()
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
    try:
        soup = start_browser()
    except Exception as e:
        print('Issue found:', e)
        download_chromedriver()
        soup = start_browser()
    print('Done! Parsing source page now...\n')
    parse(soup)
