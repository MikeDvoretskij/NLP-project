import pandas as pd
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from joblib import Parallel, delayed
from bs4 import BeautifulSoup
from tqdm import tqdm
import os

data = pd.read_csv("../data/all_links.csv")
data = data.loc[data["typeName"] == "AZƏRBAYCAN RESPUBLİKASI PREZİDENTİNİN FƏRMANLARI"].reset_index(drop=True)
data["id"] = data["id"].apply(lambda x: f"https://e-qanun.az/framework/{x}")

options = ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')

def process(data:pd.DataFrame) -> dict:
    url = str(data["id"])
    driver = Chrome(options=options)
    wait = WebDriverWait(driver, 5)
    try:
        driver.get(url)

        try:
            element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "WordSection1")))
        except Exception:
            element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "Section1")))

        soup = BeautifulSoup(driver.page_source, "lxml")
        driver.close()
        driver.quit()

        try:
            data_section = soup.find("div", class_="WordSection1")
            data_section = list(data_section.children)
            data_section = [i.text for i in data_section if i != '\n']
            data_section = "\n".join(data_section)
            return {"url": data["id"], "title": data["title"], "typeName": data["typeName"], "text": data_section}

        except AttributeError:
            data_section = soup.find("div", class_="Section1")
            data_section = list(data_section.children)
            data_section = [i.text for i in data_section if i != '\n']
            data_section = "\n".join(data_section)
            return {"url": data["id"], "title": data["title"], "typeName": data["typeName"], "text": data_section}

        except Exception as e:
            print(e)

    except Exception as e:
        print(e)

    return {"url": data["id"], "title": data["title"], "typeName": data["typeName"], "text": None}

data = Parallel(n_jobs=20)(delayed(process)(dt) for index, dt in tqdm(data.iterrows()))
data = pd.DataFrame(data)
data.to_csv("../data/decrees_of_the_president_of_the_republic_of_azerbaijan.csv", index=False, header=not os.path.exists("../data/decrees_of_the_president_of_the_republic_of_azerbaijan.csv"))

