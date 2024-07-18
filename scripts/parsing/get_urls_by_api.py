import requests
import json
import pandas as pd

start = 100
url = f"https://api.e-qanun.az/getDetailSearch?start=0&length={100}&orderColumn=8&orderDirection=desc&title=true&codeType=1&dateType=1&statusId=1&secondType=2&specialDate=false&array="
text = json.loads(requests.get(url).text)

url = url.replace(str(start), str(text["totalCount"]))
text = json.loads(requests.get(url).text)

data = pd.json_normalize(text["data"]).drop(
    ["rowNum", "citation", "effectDate",
     "registerCode", "registerDate", "htmlPath",
     "fields", "relation", "classCodes"], axis=1)

data.to_csv("../data/all_links.csv", index=False)