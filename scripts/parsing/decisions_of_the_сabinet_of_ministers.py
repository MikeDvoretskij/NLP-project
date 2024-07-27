import pandas as pd
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from joblib import Parallel, delayed
from bs4 import BeautifulSoup
from tqdm import tqdm

data = pd.read_csv("../data/all_links.csv")
data = data.loc[data["typeName"] == "AZƏRBAYCAN RESPUBLİKASI NAZİRLƏR KABİNETİNİN QƏRARLARI"].reset_index(drop=True)
data["id"] = data["id"].apply(lambda x: f"https://e-qanun.az/framework/{x}")

options = ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
def remove_if_less_by_one(nums):
    # Edge case: if the list is empty or has only one element, return it as is.
    if len(nums) < 2:
        return nums

    # Initialize the result list
    result = []

    # Iterate through the list
    for i in range(len(nums) - 1):
        # Check if the current element is less by 1 compared to the next element
        if nums[i] + 1 != nums[i + 1]:
            result.append(nums[i])

    # Add the last element since it doesn't have a next element to compare with
    result.append(nums[-1])

    return result

def process(data:pd.DataFrame) -> list[dict]:
    url = str(data["id"])
    driver = Chrome(options=options)
    wait = WebDriverWait(driver, 10)

    try:
        driver.get(url)
        try:
            element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "WordSection1")))
        except:
            element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "Section1")))

        del element

        soup = BeautifulSoup(driver.page_source, "lxml")
        driver.close()
        driver.quit()

        parts_list = []
        text_list = []

        try:
            try:
                data_section = soup.find("div", class_="WordSection1").find_all("p")
            except:
                data_section = soup.find("div", class_="Section1").find_all("p")

            for index, value in enumerate(data_section):
                if value.text.strip().find("Maddə") == 0:
                    parts_list.append(index)
                elif value.text.strip().find("M a d d ə") == 0:
                    parts_list.append(index)
                elif value.text.strip().find("a d d ə") == 0:
                    parts_list.append(index)
                elif value.text.strip().find("maddə") == 0:
                    parts_list.append(index)
                text_list.append(value.text)
            parts_list = remove_if_less_by_one(parts_list)

            parts = []

            if len(parts_list) > 0:
                for index, value in enumerate(parts_list):
                    try:
                        start = value
                        finish = parts_list[index + 1]
                        parts.append("\n".join(text_list[start:finish]))
                    except:
                        start = value
                        parts.append("\n".join(text_list[start:]))
            else:
                parts.append("\n".join(text_list))

            result = []

            for index, value in enumerate(parts):
                result.append({"url": data["id"], "title": data["title"], "typeName": data["typeName"], "text": value})

            return result

        except Exception as e:
            print(e)

    except Exception as e:
        print(e)

    return [{"url": data["id"], "title": data["title"], "typeName": data["typeName"], "text": None}]


dt = Parallel(n_jobs=-1)(delayed(process)(dt) for index, dt in tqdm(data.iterrows()))
data = []

for i in dt:
    for g in i:
        data.append(g)

data = pd.DataFrame(data=data)
data.to_csv("../data/decisions_of_the_сabinet_of_ministers.csv", index=False,)