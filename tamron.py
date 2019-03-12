import requests
import csv
from bs4 import BeautifulSoup

def read(url):
    r = requests.get(url)
    r.encoding = r.apparent_encoding
    return BeautifulSoup(r.content, 'html.parser')

def parse_toppage(html):
    lenses = []
    for lensBlock in html.find_all('div', class_='lensBlock'):
        for col in lensBlock.find_all('div', class_='col'):
            url = col.find('a')['href']
            name = col.find('div', class_='title').string
            if url[0:4] != 'http':
                url = 'https://www.tamron.jp' + url
            lenses.append({
                'name': name,
                'url': url
            })
    return lenses

def parse_subpage(url):
    if url[0:5] == 'https':
        html = read(url)
        overview = html.find('h2', class_='overview_header')
        if overview is None:
            return None
        else:
            return ''.join(list(map(lambda s: s.strip(), overview.strings)))
    else:
        return None  # 古い形式のページでは、レンズポエムを取得できない

if __name__ == '__main__':
    url = 'https://www.tamron.jp/product/'
    lenses = parse_toppage(read(url))

    for lens in lenses:
        print(lens['name'])
        lens['poem'] = parse_subpage(lens['url'])

    with open('tamron.csv', 'w') as fout:
         csv = csv.writer(fout, quoting=csv.QUOTE_NONNUMERIC)
         csv.writerow(['name', 'url', 'poem'])
         for lens in lenses:
             csv.writerow([lens['name'], lens['url'], lens['poem']])
