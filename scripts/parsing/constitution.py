import time
import pandas as pd
from selenium.webdriver import Chrome, ChromeOptions

from bs4 import BeautifulSoup
import os

data = pd.read_csv("../data/all_links.csv")
data = data.loc[data["typeName"] == "Konstitusiya"].reset_index(drop=True)
data["id"] = data["id"].apply(lambda x: f"https://e-qanun.az/framework/{x}")

options = ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')

def process(data:pd.DataFrame) -> dict:
    url = data["id"]
    driver = Chrome(options=options)
    driver.get(url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "lxml")
    driver.close()
    driver.quit()

    soup = list(soup.find("div", class_="WordSection1").children)
    p = []
    h4 = []

    for index, value in enumerate(soup):
        if value.name == 'h4':
            p.append(index)
            h4.append(index)
        elif value.name == 'p' and 'Mecelle' in value.get('class', []):
            p.append(index)

    h4 = h4[0::2]

    parts = []
    sentenses = []

    for index, value in enumerate(h4):
        try:
            start = p.index(value)
            finish = p.index(h4[index + 1])
            parts.append(p[start:finish])
        except:
            start = p.index(value)
            parts.append(p[start:])

    for part in parts:
        lst = []
        for index in part:
            lst.append(soup[index].text)
        sentenses.append("\n".join(lst))

    result = []

    for i in sentenses:
        result.append({"url": data["id"], "title": data["title"], "typeName": data["typeName"], "text": i})

    return result

data = pd.DataFrame(process(data.loc[0]))
data.to_csv("../data/constitution.csv", index=False, header=not os.path.exists("../data/constitution.csv"))