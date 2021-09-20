import datetime
import json
import os
import threading
import time
import traceback

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from telegram import InputMediaPhoto
from telegram.ext import Updater

t = 1
timeout = 5
monitor = 5
debug = False

headless = False
images = False
maximize = False

incognito = False
testing = False
fb = 'https://www.facebook.com/marketplace/denver/vehicles?sortBy=creation_time_descend&exact=false'
tkn = 'YourTelegramToken'
chat_id = -1101010101010 # Your Chat ID
updater = Updater(tkn, use_context=True)

plock = threading.Lock()
slock = threading.Lock()


def main():
    # logo()
    driver = getChromeDriver()
    item = getChromeDriver(udd="C:/items")
    driver.get(fb)
    cars = [a.text for a in getElements(driver, '//a[contains(@href,"marketplace/item")]')]
    print("Cars", cars)
    cars.pop(0)
    # cars.clear()
    while True:
        try:
            driver.get(fb)
            print(datetime.datetime.now(), "Checking...")
            for car in getElements(driver, '//a[contains(@href,"marketplace/item")]'):
                if car.text not in cars:
                    data = {
                        "msg": car.text,
                        "url": car.get_attribute('href').split("?")[0]
                    }
                    send(data)
                    threading.Thread(target=process, args=(item, data,)).start()
                    cars.append(car.text)
            time.sleep(monitor)
        except:
            traceback.print_exc()


def process(item, data):
    with plock:
        item.get(data['url'])
        data['desc'] = getElement(item, '//*[@name="google-site-verification"]/../div[2]').text
        data['img'] = [img.get_attribute('src') for img in
                       item.find_elements_by_xpath('//div[contains(@aria-label,"Thumbnail ")]/div/img')]
        send(data)


def send(data):
    threading.Thread(target=sendThread, args=(data,)).start()


def sendThread(data):
    with slock:
        print("Sending", json.dumps(data, indent=4))
        msg = f"{data['url']}\n{data['msg']}"
        if "img" in data.keys() and len(data['img']) > 0:
            imgs = [InputMediaPhoto(data['img'][0], caption=msg)]
            imgs.extend([InputMediaPhoto(x) for x in data['img'][1:10]])
            updater.bot.send_media_group(chat_id=chat_id, media=imgs)
            updater.bot.send_message(chat_id=chat_id, text=data['desc'])
        else:
            updater.bot.send_message(chat_id=chat_id, text=msg)


def click(driver, xpath, js=False):
    time.sleep(1)
    if js:
        driver.execute_script("arguments[0].click();", getElement(driver, xpath))
    else:
        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath))).click()


def getElement(driver, xpath):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))


def getElements(driver, xpath):
    return WebDriverWait(driver, timeout).until(EC.presence_of_all_elements_located((By.XPATH, xpath)))


def sendkeys(driver, xpath, keys, js=False):
    if js:
        driver.execute_script(f"arguments[0].value='{keys}';", getElement(driver, xpath))
    else:
        getElement(driver, xpath).send_keys(keys)


def getChromeDriver(port=9222, proxy=None, udd="C:/selenium"):
    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-data-dir={udd}")
    if debug:
        # print("Connecting existing Chrome for debugging...")
        options.debugger_address = f"127.0.0.1:{port}"
    else:
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-blink-features")
        options.add_argument("--disable-blink-features=AutomationControlled")
    if not images:
        # print("Turning off images to save bandwidth")
        options.add_argument("--blink-settings=imagesEnabled=false")
    if headless:
        # print("Going headless")
        options.add_argument("--headless")
        options.add_argument("--window-size=1920x1080")
    if maximize:
        # print("Maximizing Chrome ")
        options.add_argument("--start-maximized")
    if proxy:
        # print(f"Adding proxy: {proxy}")
        options.add_argument(f"--proxy-server={proxy}")
    if incognito:
        # print("Going incognito")
        options.add_argument("--incognito")
    return webdriver.Chrome(options=options)


def getFirefoxDriver():
    options = webdriver.FirefoxOptions()
    if not images:
        # print("Turning off images to save bandwidth")
        options.set_preference("permissions.default.image", 2)
    if incognito:
        # print("Enabling incognito mode")
        options.set_preference("browser.privatebrowsing.autostart", True)
    if headless:
        # print("Hiding Firefox")
        options.add_argument("--headless")
        options.add_argument("--window-size=1920x1080")
    return webdriver.Firefox(options)


def logo():
    os.system('color 0a')
    print("""
     ____  ____    _  _   __   ____  __ _  ____  ____  ____  __     __    ___  ____ 
    (  __)(  _ \  ( \/ ) / _\ (  _ \(  / )(  __)(_  _)(  _ \(  )   / _\  / __)(  __)
     ) _)  ) _ (  / \/ \/    \ )   / )  (  ) _)   )(   ) __// (_/\/    \( (__  ) _) 
    (__)  (____/  \_)(_/\_/\_/(__\_)(__\_)(____) (__) (__)  \____/\_/\_/ \___)(____)
==========================================================================================
           FB marketplace cars alert sender by fiverr.com/muhammadhassan7
==========================================================================================
[+] Monitor fb marketplace
[+] Send alert over Telegram
[+] 24/7 running...
_________________________________________________________________________________
""")


if __name__ == "__main__":
    main()
