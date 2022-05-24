import os
import re
import time
import selenium
import pandas as pd
from typing import List
from selenium import webdriver
from click import password_option
from lib2to3.pgen2 import driver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webelement import WebElement

from App import App
from Owner import Owner

# constants
account = 'enter account here'
password = 'enter password here'
phase: int = 0  # range [0, 6) for ECL, modify phase
domain = 'https://portal.azure.cn'
app_list_url = domain + \
    '/#blade/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/RegisteredApps'
driverPath = 'F:\SelfFileBackUp\Ecolab\App registration\src\chromedriver.exe'
output_file = 'F:\SelfFileBackUp\Ecolab\App registration\data\out_data' + \
    str(phase) + '.xlsx'
ht = 3488       # height + top

service = Service(driverPath)
chrome_option = Options()
# chrome_option.add_argument('--headless')  # config option
# chrome_option.add_argument('--disable-gpu')
driver = webdriver.Chrome(
    service=service, options=chrome_option)  # call the Chrome with parameters


def login(account, password):
    print('login() excuting...')
    driver.get(domain)
    time.sleep(1)

    # input account
    driver.find_element(by=By.ID, value='i0116').send_keys(account)
    driver.find_element(by=By.ID, value='idSIButton9').click()
    time.sleep(1)

    # input password
    driver.find_element(by=By.ID, value='i0118').send_keys(password)
    driver.find_element(by=By.ID, value='idSIButton9').click()
    time.sleep(10)

    driver.find_element(by=By.ID, value='idSIButton9').click()
    time.sleep(2)

    print('login() excuted.')


def get_app_list():
    print('get_app_list() excuting ...')

    driver.get(app_list_url)
    time.sleep(5)
    # element_xpath = '/html/body/div[1]/div[4]/main/div[3]/div[2]/section/div[1]/div[2]/div[4]/div[2]/div/div/div[2]/div/div[2]/div[2]/div/div[2]/div[4]/div/div[1]/div[2]/div/div'
    element_xpath = '/html/body/div[1]/div[4]/main/div[3]/div[2]/section/div[1]/div[2]/div[4]/div[2]/div/div/div[2]/div/div[2]/div[2]/div/div[1]/div[2]/div/div[1]/div[1]/div[1]'
    driver.find_element(by=By.XPATH, value=element_xpath).click()
    time.sleep(1)

    # style = "height: h px; top: t px;"
    # h + t = 3488
    # 1. press 'read more' till it disappears
    loadmore_button_classname = 'ext-ad-registeredApps-loadmore'

    for i in range(0, 2):
        driver.find_element(
            by=By.CLASS_NAME, value=loadmore_button_classname).click()
        print(f'load more clicked: {i}')
        time.sleep(1)
    print('load more done.')

    # 2. click the table to focus on the table
    form = driver.find_element(
        by=By.CLASS_NAME, value='ext-ad-appslist-application-found')
    form.click()

    list_body = driver.find_element(
        by=By.CLASS_NAME, value='ext-ad-registeredApps-applist-body')
    # 3. press 'space' key to load more data into DOM till (h+t == 3488)
    page = driver.find_element(by=By.CLASS_NAME, value='fxc-gc-page')
    script_prefix = 'document.getElementsByClassName("ext-ad-registeredApps-applist-body")[0].scrollTop='
    row_xpath = '/html/body/div[1]/div[4]/main/div[3]/div[2]/section/div[1]/div[2]/div[4]/div[2]/div/div/div[2]/div/div[2]/div[2]/div/div[2]/div[3]/div/div/div[2]/div/div[2]/div[1]/div/div'

    target_top = 0
    rows_list = []

    while(True):
        height = int(re.findall(
            '\d+', page.value_of_css_property('height')).pop())
        top = int(re.findall('\d+', page.value_of_css_property('top')).pop())
        temp_ht = height + top
        print(f'h + t = {temp_ht}')

        scroll_down_script = script_prefix + str(target_top)
        driver.execute_script(scroll_down_script)
        target_top += 500
        time.sleep(1)

        temp_rows = driver.find_elements(by=By.XPATH, value=row_xpath)

        for item in temp_rows:
            if(item not in rows_list):
                rows_list.append(item)

        if temp_ht >= ht:
            print(f'length of row_list: {len(rows_list)}')
            print('scroll finished')
            break
    return rows_list


def row2owner(row: WebElement):
    name: str = row.find_element(
        by=By.XPATH, value='./div[2]/div[2]/a').get_attribute('innerText')
    email: str = row.find_element(
        by=By.XPATH, value='./div[3]/div').get_attribute('innerText')
    u_name: str = row.find_element(
        by=By.XPATH, value='./div[4]/div').get_attribute('innerText')
    title: str = row.find_element(
        by=By.XPATH, value='./div[5]/div').get_attribute('innerText')
    type: str = row.find_element(
        by=By.XPATH, value='./div[6]/div').get_attribute('innerText')

    return Owner(name=name, email=email, u_name=u_name, title=title, type=type)


def get_owner_list(app_id: str):
    # Owner Page
    owner_url = domain + \
        '/#blade/Microsoft_AAD_RegisteredApps/ApplicationMenuBlade/Owners/appId/' + \
        app_id + '/isMSAApp/'
    driver.get(owner_url)
    time.sleep(3)

    owners = []

    owner_pages = driver.find_elements(by=By.CLASS_NAME, value='fxc-gc-page')
    # directly return when there is no owner displayed
    # print(len(owner_pages))
    if len(owner_pages) == 0:
        return owners

    owner_rows = owner_pages[0].find_elements(
        by=By.CLASS_NAME, value='fxc-gc-row-content')
    for row in owner_rows:
        temp_owner = row2owner(row=row)
        owners.append(temp_owner)
    return owners


def deep_app(created: str, secrets: str, overview_url: str):
    # overview_url = 'https://portal.azure.cn/#blade/Microsoft_AAD_RegisteredApps/ApplicationMenuBlade/Overview/appId/' + app_id + '/isMSAApp/'
    # driver.get(overview_url)
    # open and switch to overview window
    overview_js = 'window.open("' + overview_url + '");'
    driver.execute_script(overview_js)
    handles = (driver.window_handles)
    driver.switch_to.window(handles[1])
    time.sleep(3)
    # to avoid anti-crawler, sleep longer
    # time.sleep(10)

    container = driver.find_elements(
        by=By.CLASS_NAME, value='fxc-essentials-column-container')[0]

    # left side
    name = container.find_element(
        by=By.XPATH, value='./div[3]/div[1]/div[3]/div/div/a').get_attribute('innerText')
    app_id: str = container.find_element(
        by=By.XPATH, value='./div[3]/div[2]/div[3]/div/div/div[1]').get_attribute('innerText')
    obj_id: str = container.find_element(
        by=By.XPATH, value='./div[3]/div[3]/div[3]/div/div/div[1]').get_attribute('innerText')
    dir_id: str = container.find_element(
        by=By.XPATH, value='./div[3]/div[4]/div[3]/div/div/div[1]').get_attribute('innerText')
    type: str = container.find_element(
        by=By.XPATH, value='./div[3]/div[5]/div[3]/div/div/a').get_attribute('innerText')

    # right side
    cred: str = container.find_element(
        by=By.XPATH, value='./div[4]/div[1]/div[3]/div/div/a').get_attribute('innerText')
    re_uri: str = container.find_element(
        by=By.XPATH, value='./div[4]/div[2]/div[3]/div/div/a').get_attribute('innerText')
    app_id_uri: str = container.find_element(
        by=By.XPATH, value='./div[4]/div[3]/div[3]/div/div/a').get_attribute('innerText')
    # index = 74, app_local not found
    # app_local: str = container.find_element(
    #     by=By.XPATH, value='./div[4]/div[4]/div[3]/div/div/a').get_attribute('innerText')
    app_local: str = ''

    owners = get_owner_list(app_id=app_id)

    # to avoid anti-crawler, sleep longer
    # time.sleep(10)
    # close detail window
    driver.close()
    driver.switch_to.window(handles[0])

    print(name, app_id, created, len(owners))
    return App(created=created, secrets=secrets, name=name,
               app_id=app_id, obj_id=obj_id, dir_id=dir_id,
               type=type, cred=cred, re_uri=re_uri,
               app_id_uri=app_id_uri, app_local=app_local, owners=owners)


def row2app(row: WebElement):
    created: str = row.find_element(
        by=By.XPATH, value='./div[1]/div[4]/div').get_attribute('innerText')
    secrets: str = row.find_element(
        by=By.XPATH, value='./div[1]/div[5]/div/span[2]').get_attribute('innerText')
    app_id: str = row.find_element(
        by=By.XPATH, value='./div[1]/div[3]/div').get_attribute('innerText')

    overview_url = domain + \
        '/#blade/Microsoft_AAD_RegisteredApps/ApplicationMenuBlade/Overview/appId/' + \
        app_id + '/isMSAApp/'
    app = deep_app(created=created, secrets=secrets, overview_url=overview_url)
    return app


def organize_data(rows_list: list):
    apps = list()
    size_int: int = len(rows_list)
    size_str: str = str(size_int)

    start: int = phase * 20
    for index in range(0, 20):
        real_index = index + start
        if (real_index >= (size_int - 1)):
            break
        row = rows_list[real_index]

        print('app: ' + str(real_index) + ' / ' + size_str)
        tmp_app = row2app(row=row)
        apps.append(tmp_app)

    # quit from browser
    driver.quit
    return apps


def output_apps(apps: list):
    # transform app list into dictionary
    app_dic = {'name': [], 'owners': [], 'secrets': []}
    for app in apps:
        app_dic['name'].append(app.name)
        owners = app.get_owners()
        app_dic['owners'].append(owners)
        app_dic['secrets'].append(app.secrets)

    # if the output file has existed, then delete it
    if os.path.exists(output_file):
        os.remove(output_file)
        print('file removed: ' + output_file)

    # write dictionary into excel file
    file_writer = pd.ExcelWriter(output_file)
    app_dic = pd.DataFrame(app_dic)
    app_dic.to_excel(excel_writer=file_writer, sheet_name='sheet1')
    file_writer.save()


login(account=account, password=password)
rows_list = get_app_list()
apps = organize_data(rows_list=rows_list)
output_apps(apps=apps)
