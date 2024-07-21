import pandas as pd
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from joblib import Parallel, delayed
from bs4 import BeautifulSoup
from tqdm import tqdm

data = pd.read_csv("../data/all_links.csv")
data = data.loc[data["typeName"] == "Referendum aktları"].reset_index(drop=True)
data["id"] = data["id"].apply(lambda x: f"https://e-qanun.az/framework/{x}")

options = ChromeOptions()
# options.add_argument('--headless')
# options.add_argument('--disable-gpu')

def process(data:pd.DataFrame) -> list[dict]:
    url = str(data["id"])
    driver = Chrome(options=options)
    wait = WebDriverWait(driver, 30)

    try:
        driver.get(url)
        element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "WordSection1")))

        soup = BeautifulSoup(driver.page_source, "lxml")
        driver.close()
        driver.quit()

        try:
            data_section = soup.find("div", class_="WordSection1").find_all("p")
            data_section = "\n".join([i.text for i in data_section])
            return {"url": data["id"], "title": data["title"], "typeName": data["typeName"], "text": data_section}

        except Exception as e:
            print(e)

    except Exception as e:
        print(e)

    return {"url": data["id"], "title": data["title"], "typeName": data["typeName"], "text": None}


data = Parallel(n_jobs=3)(delayed(process)(dt) for index, dt in tqdm(data.iterrows()))


data = pd.DataFrame(data=data)
print(data)
data.to_csv("../data/referendum_acts.csv", index=False)