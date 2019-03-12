import requests
import csv
from bs4 import BeautifulSoup

def read(url):
    r = requests.get(url)
    r.encoding = r.apparent_encoding
    return BeautifulSoup(r.content, 'html.parser')

def parse_toppage(html):
    lenses = []
    for ul in html.find_all('ul', class_='mod-goodsList-ul'):
        for li in ul.find_all('li'):
            a = li.find('a')
            img = li.find('img')
            if a is not None and img is not None:
                url = a['href']
                name = img['alt']
                lenses.append({
                    'name': name,
                    'url': 'https://www.nikon-image.com' + url
                })
    return lenses

def parse_subpage(html):
    p = html.find('div', class_='mod-productHero-detail').find('p')
    texts = list(p.strings)
    return texts[0]

if __name__ == '__main__':
    lenses = parse_toppage(read('https://www.nikon-image.com/products/nikkor/fmount/'))
    lenses.extend(parse_toppage(read('https://www.nikon-image.com/products/nikkor/zmount/')))

    for lens in lenses:
        print(lens['name'])
        lens['poem'] = parse_subpage(read(lens['url']))

    with open('nikon.csv', 'w') as fout:
        csv = csv.writer(fout, quoting=csv.QUOTE_NONNUMERIC)
        csv.writerow(['name', 'url', 'poem'])
        for lens in lenses:
            csv.writerow([lens['name'], lens['url'], lens['poem']])
