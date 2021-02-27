from typing import List
from functools import partial

import arrow
import requests
import json
import os
from bs4 import BeautifulSoup
from pathlib import Path

BeautifulSoup = partial(BeautifulSoup, features="html.parser")
os.chdir(Path(__file__).parent)

PRTS_OPS_URL = "http://prts.wiki/w/%E5%B9%B2%E5%91%98%E4%B8%80%E8%A7%88"
PRTS_TIMES_URL = "http://prts.wiki/w/%E5%B9%B2%E5%91%98%E4%B8%8A%E7%BA%BF%E6%97%B6%E9%97%B4%E4%B8%80%E8%A7%88"
PRTS_BANNERS_URL = "http://prts.wiki/w/%E5%8D%A1%E6%B1%A0%E4%B8%80%E8%A7%88/%E9%99%90%E6%97%B6%E5%AF%BB%E8%AE%BF"


def remove_prefix(prefix, string):
    if isinstance(prefix, str):
        if string.startswith(prefix):
            return string[len(prefix):]
        return string
    else:
        for i in prefix:
            if string.startswith(i):
                return string[len(i):]
        return string


def remove_suffix(string, suffix):
    if isinstance(suffix, str):
        if string.endswith(suffix):
            return string[:-len(suffix)]
        return string
    else:
        for i in suffix:
            if string.endswith(i):
                return string[:-len(i)]
        return string


def get_banners_info():
    res = requests.get(PRTS_BANNERS_URL)
    soup = BeautifulSoup(res.text)

    result = []
    for tr in soup.find_all("tr"):
        children = tuple(filter(lambda i: not isinstance(i, str), tr.contents))
        temp = {}
        if "卡池一览" not in children[0].text and children[0].a:
            temp["name"] = remove_prefix(
                "寻访模拟/", children[0].find_all("a")[~0]["title"])
            time = children[1].text
            try:
                time = time[:time.index(" ")]
            except:
                time = None
            else:
                time = arrow.get(time, "YYYY.MM.DD").format("YYYYMMDD")
            temp["time"] = time
            rateups = []
            for i in children[~0].find_all("a") + children[~1].find_all("a"):
                rateups.append(i["title"])
            temp["rateups"] = rateups

            result.append(temp)
    return result


def save_banners_info() -> None:
    path = Path("../assets/arknights/banners.json")
    with path.open("w", encoding="utf-8") as f:
        f.write(json.dumps(
            get_banners_info(),
            ensure_ascii=False,
            indent=4,
        ))


def get_operators_info(
    *args,
    **kwargs,
) -> List[dict]:
    filters = kwargs.get("filters")
    if filters: del kwargs["filters"]

    all_ = False
    if kwargs.get("all"):
        all_ = True

    def filter_(str) -> bool:
        return str in [*args, *[k for k in kwargs.keys()]]

    rename_map = {arg: arg for arg in args}
    rename_map.update(kwargs)

    if all_:
        filter_ = lambda *_: True
        rename_map = None

    res = requests.get(PRTS_OPS_URL)
    soup = BeautifulSoup(res.text)

    result = []
    temp_operators = dict()
    for op in soup.find_all(class_="smwdata"):
        del op.attrs["class"]
        temp = {
            rename_map[remove_prefix("data-", k)]
            if rename_map else remove_prefix("data-", k): v
            for k, v in op.attrs.items()
            if filter_((remove_prefix("data-", k)))
        }
        result.append(temp)
        if all_ or "time" in rename_map:
            temp_operators[op["data-cn"]] = temp

    if temp_operators:
        res = requests.get(PRTS_TIMES_URL)
        soup = BeautifulSoup(res.text)
        for tag in soup.find_all("tr")[1:]:
            children = tuple(
                filter(lambda i: not isinstance(i, str), tag.contents))

            name = children[0].a["title"]
            time = arrow.get(children[2].string,
                             "YYYY-M-DTHH:mm:ss").format("YYYYMMDD")
            if temp_operators.get(name):
                temp_operators[name][
                    rename_map["time"] if rename_map else "time"] = time

    if filters:
        for op in result:
            for k in filters.keys():
                op[k] = filters[k](op[k])

    return result


def save_operators_info(less: bool = True) -> None:
    path = f"../assets/arknights/operators{'_less' if less else ''}.json"
    path = Path(path)

    if less:
        with path.open("w", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    get_operators_info(
                        "approach",
                        "class",
                        "rarity",
                        cn="cn_name",
                        en="en_name",
                        time="release_time",
                        filters={
                            "rarity": lambda i: int(i) + 1,
                        },
                        all=not less,
                    ),
                    ensure_ascii=False,
                    indent=4,
                ))


if __name__ == "__main__":
    from pprint import pprint
    # pprint(get_operator_infos("approach", "class", "rarity", cn="cn_name"))
    # pprint(get_operator_infos(all=True))
    # get_operator_infos(all=True)
    # pprint(
    #     get_operators_info(
    #         "approach",
    #         "class",
    #         "rarity",
    #         time="release_time",
    #         cn="cn_name",
    #     ))
    # pprint(get_banners_info())
    save_operators_info()
    save_banners_info()
