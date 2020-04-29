import json
from pathlib import Path
import re
from lxml.etree import HTML
import requests


class Login:
    urls = {
        'ids': 'http://ids.xidian.edu.cn/authserver/login',
        'apps': 'http://ehall.xidian.edu.cn/jsonp/getUserAllUsableApp',
        'app': 'http://ehall.xidian.edu.cn//appShow',
        'test': 'http://ids.xidian.edu.cn/authserver/userAttributesEdit.do',
    }

    def __init__(self, username=None, password=None, cookies=None):
        self.username = username
        self.password = password
        self._session = requests.Session()
        self.session.headers.update({
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,kk;q=0.7',
            'Accept-Encoding': 'gzip, deflate',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'
        })
        if cookies:
            self.session.cookies.update(cookies)

    @property
    def session(self):
        return self._session

    def ids_get_tokens(self):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Host': 'ids.xidian.edu.cn',
            'Upgrade-Insecure-Requests': '1',
        }
        res = self.session.get(self.urls['ids'], headers=headers)
        if res.status_code == 200:
            html = HTML(res.text)
            hidden_inputs = html.xpath('//input[@type="hidden"]')
            return {i.xpath('@name')[0]: i.xpath('@value')[0] for i in hidden_inputs if i.xpath('@value!="unknown"')}
        return False

    def ids_login(self):
        form_data = {'username': self.username, 'password': self.password}
        form_data.update(self.ids_get_tokens())
        res = self.session.post(
            'http://ids.xidian.edu.cn/authserver/login', data=form_data)
        if res.status_code == 200:
            return self.status
    
    @property
    def apps(self):
        res = self.session.get(self.urls['apps'])
        return res.json()['data']

    def request_app(self, app_name):
        for i in self.apps:
            if i['appName'] == app_name:
                app_id = i['appId']
                res = self.session.get(self.urls['app'], params={'appId': app_id})
                break

    @property
    def status(self):
        res = self.session.get(self.urls['test'], allow_redirects=False)
        if res.status_code == 200 and (m := re.search(r'userId=(?P<username>\d{11})"', res.text, re.S)) is not None:
            return m.group('username')

    @property
    def cookies(self):
        return self.session.cookies

    def save_cookies(self):
        path = Path.home() / '.xdutools'
        path.mkdir(exist_ok=True)
        (path / 'cookies.json').write_text(json.dumps(self.session.cookies.get_dict()))

    @classmethod
    def by_cookies(cls):
        cookies = Path.home() / '.xdutools'/'cookies.json'
        cookies.touch()
        return cls(cookies=json.loads(cookies.read_text()))
