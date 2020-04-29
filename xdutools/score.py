import json

query = [{
    "name": "XNXQDM",
    "value": "2019-2020-1",
    "linkOpt": "and",
    "builder": "m_value_equal"
}, {
    "name": "SFYX",
    "caption": "是否有效",
    "linkOpt": "AND",
    "builderList": "cbl_m_List",
    "builder": "m_value_equal",
    "value": "1",
    "value_display": "是"
}, {
    "name": "SHOWMAXCJ",
    "caption": "显示最高成绩",
    "linkOpt": "AND",
    "builderList": "cbl_m_List",
    "builder": "m_value_equal",
    "value": "0",
    "value_display": "否"
}]

URLS = {
    'cj': 'http://ehall.xidian.edu.cn/jwapp/sys/cjcx/modules/cjcx/xscjcx.do',
}
APP_NAME = '成绩查询'


class Score(object):
    def __init__(self):
        pass

    def get_scores(self, session, term='2019-2020-1'):
        query[0].update(value=term)
        res = session.post(URLS['cj'], data={'querySetting': query})
        return map(self.process_score, res.json()['datas']['xscjcx']['rows'])

    def process_score(self, score):
        return {
            'lesson': score['KCM'],
            'final': score['ZCJ'],
            'effective': bool(int(score['SFYX'])),
            'pass': bool(int(score['SFJG'])),
        }

    def save_scores(self, scores):
        with open('./scores.json', 'w', encoding='utf-8') as fp:
            json.dump([i for i in scores], fp, ensure_ascii=False, indent=4)
