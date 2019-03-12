import requests
import csv
from bs4 import BeautifulSoup

def read(url):
    r = requests.get(url)
    r.encoding = r.apparent_encoding
    return BeautifulSoup(r.content, 'html.parser')

def parse_toppage(html):
    lenses = []
    for id in ['contemporary', 'art', 'sports', 'others']:
        for li in html.find('section', id=id).find_all('li'):
            url = li.find('a')['href']
            name = li.find('b').string
            lenses.append({
                'name': name,
                'url': 'https://www.sigma-global.com' + url
            })
    return lenses

def parse_subpage(html):
    return html.select('meta[name="description"]')[0]['content']

if __name__ == '__main__':
    url = 'https://www.sigma-global.com/jp/lenses/'
    lenses = parse_toppage(read(url))

    for lens in lenses:
        print(lens['name'])
        lens['poem'] = parse_subpage(read(lens['url']))

    with open('sigma.csv', 'w') as fout:
         csv = csv.writer(fout, quoting=csv.QUOTE_NONNUMERIC)
         csv.writerow(['name', 'url', 'poem'])
         for lens in lenses:
             csv.writerow([lens['name'], lens['url'], lens['poem']])
