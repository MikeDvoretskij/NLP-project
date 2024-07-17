from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from bs4 import BeautifulSoup

import time

start_url = "https://e-qanun.az/"

def get_element_xpath(element):
    components = []
    while element is not None:
        siblings = element.find_previous_siblings(element.name)
        count = len(siblings) + 1
        components.append(element.name if count == 1 else '%s[%d]' % (element.name, count))
        element = element.find_parent()
    return '/%s' % '/'.join(reversed(components))


def urls(start:str, category:str) -> [str]:
    options = ChromeOptions()
    driver = Chrome(options=options)

    category = category.split("/")
    category = category if len(category) > 1 else category[0]

    driver.get(start)
    time.sleep(5)

    button = driver.find_element(By.CLASS_NAME, "rct-node-clickable")
    button.click()

    def target_element(soup, index, name, class_):
        target_element = soup.find("span", string=category[index]).find_parent(name, class_=class_)

        if target_element is not None :
            xpath = get_element_xpath(target_element)
            xpath = xpath.replace('/[document]', '')
            return xpath

        else:
            target_element = soup.find("span", string=category[index]).find_parent("span", class_="rct-text").find("span", role="checkbox")
            xpath = get_element_xpath(target_element)
            xpath = xpath.replace('/[document]', '')
            return xpath

    if type(category) is list:
        soup = BeautifulSoup(driver.page_source, "lxml")
        button = driver.find_element(By.XPATH, target_element(soup=soup, index=0, name="span", class_="rct-node-clickable"))
        button.click()
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "lxml")
        checkbox = driver.find_element(By.XPATH, target_element(soup=soup, index=1, name="plmvrs", class_="oifes"))
        if not checkbox.is_selected():
            checkbox.click()

        button = driver.find_element(By.CLASS_NAME, "Header-search__button")
        button.click()
    else:
        soup = BeautifulSoup(driver.page_source, "lxml")
        target_el = soup.find("span", string=category).find_parent("span", class_="rct-text").find("span", role="checkbox")
        xpath = get_element_xpath(target_el)
        xpath = xpath.replace('/[document]', '')

        checkbox = driver.find_element(By.XPATH, xpath)
        if not checkbox.is_selected():
            checkbox.click()

        button = driver.find_element(By.CLASS_NAME, "Header-search__button")
        button.click()

    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "lxml")
    links = soup.find("div", class_="Result_Result__hBwLN MuiBox-root css-0").find_all("a")
    links = list(map(lambda x: f"https://e-qanun.az{x.get('href')}", links))
    print(links)

    driver.close()
    driver.quit()
    return links

urls(start_url, "AZƏRBAYCAN RESPUBLİKASININ KONSTİTUSİYASI VƏ REFERENDUM AKTLARI (9)")

