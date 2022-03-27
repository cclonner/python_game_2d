import requests
from bs4 import BeautifulSoup

URL = "https://bsgclub.admin.enes.tech/"
HEADERS = {
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Mobile Safari/537.36',
    'accept': '*/*'}


# https://bsgclub.admin.enes.tech/cashbox/o/2/073903/refill/check
# {
#    'user-agent': '(Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Mobile Safari/537.36',
#    'accept': '*/*'}
def get_html(url, params=None) -> requests.Response:
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def get_content(html):
    soup = BeautifulSoup(html.text, 'html.parser')
    items = soup.find_all('span', class_='u-h2 dashboard-title')
    print(items)


def parse():
    html = get_html(URL)
    print(html.status_code)
    if html.status_code == 200:
        get_content(html)
    else:
        print("error ")


parse()


