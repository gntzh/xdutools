import requests
from lxml.etree import HTML


class Login:
    urls = {
        'ids': 'http://ids.xidian.edu.cn/authserver/login',
        'apps': 'http://ehall.xidian.edu.cn/jsonp/getUserAllUsableApp',
        'app': 'http://ehall.xidian.edu.cn//appShow'
    }

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self._session = requests.Session()
        self.session.headers.update({
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,kk;q=0.7',
            'Accept-Encoding': 'gzip, deflate',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'
        })

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
            html = HTML(res.text)
            return True
        return False

    def get_apps(self):
        res = self.session.get(self.urls['apps'])
        return res.json()['data']

    def get_app_id(self, app_name):
        apps = self.get_apps()
        app_id = [i for i in apps if i['appName'] == app_name][0]['appId']
        return app_id

    def request_app(self, app_name):
        res = self.session.get(self.urls['app'], params={
                               'appId': self.get_app_id(app_name)})

    @property
    def cookies(self):
        return self.session.cookies
