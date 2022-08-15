import asyncio
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import random
import subprocess
import json
import requests



def authentication():
    current_machine_id = str(subprocess.check_output('wmic csproduct get uuid'), 'utf-8').split('\n')[1].strip()
    ip = current_machine_id
    print(f'Your IP is {ip}')
    print("\n")
    url = f'http://sunnyislam.pythonanywhere.com/members/verification?uuid={ip}'
    data = requests.get(url)
    data = data.json()
    if data['message'] == 'okay':
        name = data.get('name')
        print('Authenticated!')
        print(f'Welcome {name}!')
        print(f"Use Until >>  {data['date']}\n")
        return True
    else:
        print("Not a valid user or valid date has expired")
        return False

async  def make_tabs(driver):
    #print("opening a new tab")
    driver.execute_script("window.open()")
    await asyncio.sleep(2)

def get_url(i):
    url = "https://accounts.google.com/signin/v2/recoveryidentifier?hl=en-GB&flowName=GlifWebSignIn&flowEntry=AccountRecovery"
    return url

async def get_valid_numbers(driver,i,numbers,captcha_infected_window):
    if not numbers :
        return 

    if i in captcha_infected_window:
        driver.switch_to.window(driver.window_handles[i])
        driver.refresh()
        await asyncio.sleep(10)
        captcha_infected_window.remove(i)


    number = numbers.pop()
    driver.switch_to.window(driver.window_handles[i])
    url = get_url(i)
    driver.get(url)
    input_box = driver.find_element(By.ID,"identifierId")
    input_box.clear()
    input_box.send_keys(number)
    input_box.send_keys(Keys.RETURN)
    await asyncio.sleep(3)
    driver.switch_to.window(driver.window_handles[i])
    url = get_url(i)

    if url != driver.current_url:
        with open('numbers.txt', 'a') as file:
            file.write(f"{number}\n")
        print(f"{number}:YES \n")
    
    else:
        captcha_image = driver.find_element(By.ID,"captchaimg")
        if captcha_image.is_displayed():
            print(f"OOPS! CAPTCHA FOUND: {number}")
            numbers.append(number)
            if i not in captcha_infected_window:
                captcha_infected_window.append(i)
        else:
            print(f"{number}:NO \n")

async def main(driver,numbers,length):
    event = asyncio.Event()
    await asyncio.gather(*[make_tabs(driver) for i in range(20)]) # 20 tabs
    if len(driver.window_handles)>= 20: 
        event.set()
    await event.wait()
    #print(len(driver.window_handles))
    captcha_infected_window = []
    while numbers and len(captcha_infected_window) <= 19:
        await asyncio.gather(*[get_valid_numbers(driver,i,numbers,captcha_infected_window) for i in range(len(driver.window_handles))])
    
        if len(captcha_infected_window) >= 19:
            numbers.sort()
            print(f"Due to severe captcha infection, we have terminated this session. We failed to analyse these numbers:\n {numbers}")
            numbers = []
    driver.quit()
    


t1 = time.time()
global captcha_numbers 
captcha_numbers = []
url = {}
if authentication():
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    numbers_with_gmail_account = []
    print("Enter a phone number to start")
    str_number = input() #96899431100 
    int_number = int(str_number)
    lead_zeros = len(str_number)
    print("Enter the number of iterations. 100 is recommended to avoid captcha infection.")
    length = int(input())
    numbers = [str(int_number+i).zfill(lead_zeros) for i in range(length) ]
    print("We are preparing the software to analyse data...")

    asyncio.run(main(driver,numbers,length))

    print("Finished")
    if numbers:
        print(f'We failed to analyse these numbers due to captcha infection: {numbers}')
    t2 = time.time()
    print(f"Elapsed Time:{t2-t1} seconds")
input(">>>Press Enter to exit.............")

