import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterable, List, Union

if TYPE_CHECKING:
    from httpx import AsyncClient

E_HALL_NAME = "成绩查询"
E_HALL_ID = "4768574631264620"

GRADES_URL = ("http://ehall.xidian.edu.cn/jwapp/sys/cjcx/modules/cjcx/xscjcx.do",)


query = [
    {
        "name": "XNXQDM",
        "value": "2019-2020-1",
        "linkOpt": "and",
        "builder": "m_value_equal",
    },
    {
        "name": "SFYX",
        "caption": "是否有效",
        "linkOpt": "AND",
        "builderList": "cbl_m_List",
        "builder": "m_value_equal",
        "value": "1",
        "value_display": "是",
    },
    {
        "name": "SHOWMAXCJ",
        "caption": "显示最高成绩",
        "linkOpt": "AND",
        "builderList": "cbl_m_List",
        "builder": "m_value_equal",
        "value": "0",
        "value_display": "否",
    },
]


@dataclass
class Grade(object):
    course: str
    score: Union[str, int]
    is_pass: bool

    @classmethod
    def by_data(cls, raw_data: dict):
        return cls(
            lesson=raw_data["KCM"],
            final=raw_data["ZCJ"],
            effective=bool(int(raw_data["SFYX"])),
            is_pass=bool(int(raw_data["SFJG"])),
        )


async def get_grades(client: "AsyncClient", term="2019-2020-1") -> List[Grade]:
    query[0].update(value=term)
    res = await client.post(GRADES_URL, data={"querySetting": query})
    return [Grade.by_data(i) for i in res.json()["datas"]["xscjcx"]["rows"]]


def save_scores(grades: Iterable[Grade]):
    with open("./scores.json", "w", encoding="utf-8") as fp:
        json.dump([i for i in grades], fp, ensure_ascii=False, indent=4)
