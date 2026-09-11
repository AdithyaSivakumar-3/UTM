import requests
from bs4 import BeautifulSoup

url = 'https://ju.se/en/study-at-ju/masters.html'
try:
    r = requests.get(url, timeout=10)
    print('status', r.status_code)
    soup = BeautifulSoup(r.text, 'html.parser')
    for a in soup.find_all('a', href=True):
        if 'master' in a['href']:
            print(a.text.strip(), a['href'])
except Exception as e:
    print('error', e)