import logging
import random
import requests
import time
from requests.packages import urllib3
from urllib.parse import urljoin
from bs4 import BeautifulSoup


# Disable urllib3 warning, see lord63/a_bunch_of_code#9.
urllib3.disable_warnings()

# Disable log message from the requests library.
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)


def _make_cookie(cookie_str: str) -> dict:
    return dict([i.split('=', 1) for i in cookie_str.split('; ')])


class V2ex(object):
    base_url = 'https://www.v2ex.com'
    signin_url = urljoin(base_url, '/signin')
    balance_url = urljoin(base_url, '/balance')
    mission_url = urljoin(base_url, '/mission/daily')

    def __init__(self, cookie_file):
        self.cookie_file = cookie_file
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:28.0) Gecko/20100101 Firefox/28.0',
        })
        self.load_cookie()

        self.bs4_features = "html.parser"
        try:
            import lxml
            _ = lxml
            self.bs4_features = "lxml"
        except ImportError:
            pass

    def load_cookie(self):
        with open(self.cookie_file, "r") as f:
            s = f.read().strip()
        cookies = _make_cookie(s)
        self.session.cookies.update(cookies)

    def save_cookie(self):
        cookies = dict(self.session.cookies.items())
        cookies = "; ".join(["{}={}".format(x, y) for x, y in cookies.items()])
        with open(self.cookie_file, "w") as f:
            f.write(cookies)
            f.write("\n")

    def get_money(self):
        """Complete daily mission then get the money."""
        response = self.session.get(self.mission_url, verify=False)
        soup = BeautifulSoup(response.text, self.bs4_features)
        onclick = soup.find('input', class_='super normal button')['onclick']
        url = onclick.split('=', 1)[1][2:-2]

        if url == '/balance':
            return "You have completed the mission today."
        else:
            headers = {'Referer': self.mission_url}
            data = {'once': url.split('=')[-1]}
            self.session.get(urljoin(self.baseurl, url), verify=False,
                             headers=headers, data=data)
            balance = self._get_balance()
            return balance

    def _get_balance(self):
        """Get to know how much you totally have and how much you get today."""
        response = self.session.get(self.balance_url, verify=False)
        soup = BeautifulSoup(response.text, self.bs4_features)
        first_line = soup.select(
            "table.data tr:nth-of-type(2)")[0].text.strip().split('\n')
        total, today = first_line[-2:]
        logging.info('%-26sTotal:%-8s', today, total)
        return '\n'.join(["Today: {0}".format(today),
                          "Total: {0}".format(total)])

    def get_last(self):
        """Get to know how long you have kept signing in."""
        response = self.session.get(self.mission_url, verify=False)
        soup = BeautifulSoup(response.text, self.bs4_features)
        last = soup.select('#Main div')[-1].text
        return last

    def visit(self, count, sleep=1):
        """Visit home page to increase activity level."""
        url = urljoin(self.base_url, "/")
        response = self.session.get(url, verify=False)
        soup = BeautifulSoup(response.text, self.bs4_features)
        links = soup.select('#Main a.topic-link[href^="/t/"]')
        random.shuffle(links)
        success = 0
        for i, link in enumerate(links):
            if i >= count:
                break
            url = urljoin(self.base_url, link['href'].split("#")[0])
            response = self.session.get(url, verify=False)
            if response.status_code == 200:
                success += 1
            time.sleep(sleep)
        return success
