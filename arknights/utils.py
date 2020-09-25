from typing import List
import requests
from bs4 import BeautifulSoup

PRTS_URL = "http://prts.wiki/w/%E5%B9%B2%E5%91%98%E4%B8%80%E8%A7%88"


def remove_prefix(prefix, string):
    if string.startswith(prefix):
        return string[len(prefix):]
    return string


def get_operator_infos() -> List[dict]:
    res = requests.get(PRTS_URL)
    soup = BeautifulSoup(res)

    result = []
    for op in soup.find_all(class_="smwdata"):
        temp = {
            remove_prefix("data-", k): v
            for k, v in op.attrs.items() if k != "class"
        }
        result.append(temp)

    return result
