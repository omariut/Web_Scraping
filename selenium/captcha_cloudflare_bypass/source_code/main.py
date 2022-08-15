import time
import json
import random
import asyncio
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait


def get_driver(proxies):
    PROXY = random.choice(proxies)
    proxy = {'https': f'https://{PROXY}'}
    options = uc.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument(f'--proxy-server={PROXY}')
    options.add_argument('--allow-insecure-localhost')
    caps = options.to_capabilities()
    caps["acceptInsecureCerts"] = True
    driver = uc.Chrome(options=options, use_subprocess=True, desired_capabilities = caps)
    return driver


def login_attempt(data, driver):
    url = data["url"]
    username_element_name = data["username_element_name"]
    password_element_name = data["password_element_name"]
    username = data["username"]
    password = data["password"]
    driver.get(url)

    try:
        WebDriverWait(driver, timeout=15).until(
            lambda d: d.find_element(By.NAME, username_element_name))
        username_box = driver.find_element(By.NAME, username_element_name)

    except:
        print('Something went wrong. try again after removing this proxy')
        print(f'login failed for: {url}')
        return

    username_box.clear()
    username_box.send_keys(username)
    password_box = driver.find_element(By.NAME, password_element_name)
    password_box.clear()
    password_box.send_keys(password)
    password_box.send_keys(Keys.RETURN)
    WebDriverWait(driver, timeout=5).until(
        lambda d: d.find_element(By.CLASS_NAME, "userMenu"))

    try:
        driver.find_element(By.CLASS_NAME, "userMenu")
        print(f'login success for: {url} ')
        return True
    except:
        print('login failed')
        return False


async def simultaneous_request(url, driver):
    driver.switch_to.new_window('tab')
    driver.get(url)


async def find_success_urls(tab, site_title, driver):
    success_urls = 0
    driver.switch_to.window(driver.window_handles[tab])
    
    if driver.title in site_title:
        success_urls += 1
        print(f'true')
    else:
        print('false')
    
    return success_urls


async def main():

    operation_summery = {}
    driver = get_driver(proxies)
    driver.get('https://api.ipify.org/')
    ip_address = driver.find_element(By.TAG_NAME, "body").text
    print(ip_address)

    for data in url_data:
        url = data["url"]
        site_title = data["title"]
        target_urls = data.get('target_urls')
        total_target_urls = len(target_urls)

        if login_attempt(data, driver):
            
            await asyncio.gather(*[simultaneous_request(url, driver) for url in target_urls])
            await asyncio.sleep(3)
            success_urls = await asyncio.gather(*[find_success_urls(tab, site_title, driver) for tab in range(len(driver.window_handles))])

            # prepare operation summery and pass it in a json format
            ratio = sum(success_urls) / total_target_urls
            if ratio >= 0.6:
                operation_summery[url] = True
            else:
                operation_summery[url] = False
        else:
            operation_summery[url] = False

    print(operation_summery)
    driver.quit()
    return json.dumps(operation_summery)

#main calling starts here!
with open('proxy.txt', 'r') as p_f:
    data = p_f.read()
    proxies = data.split('\n')

with open('url_data.json', 'r') as f:
    data = f.read()
    url_data = json.loads(data)["data"]
try:
    asyncio.run(main())
except:
    print('Might be an internet connection error. We are preparing the driver again.')
    time.sleep(3)
    asyncio.run(main())

