import requests
import csv
from bs4 import BeautifulSoup

def read(url):
    req = requests.Request('GET', url).prepare()
    r = requests.Session().send(req)
    r.encoding = r.apparent_encoding
    return BeautifulSoup(r.text, 'html.parser')

def parse_toppage(html):
    lenses = []
    for ul in html.find_all('ul', class_='products__series_list'):
        for li in ul.find_all('li'):
            url = li.find('a')['href']
            name = list(li.find('h3').strings)[0]
            lenses.append({'name': name, 'url': url})
    return lenses

def parse_subpage(html):
    return html.find('section', class_='productspost__first').find('p').string

if __name__ == '__main__':
    lenses = parse_toppage(read('https://fujifilm-x.com/ja-jp/lenses/'))

    for lens in lenses:
        print(lens['name'])
        lens['poem'] = parse_subpage(read(lens['url']))

    with open('fujifilm.csv', 'w') as fout:
         csv = csv.writer(fout, quoting=csv.QUOTE_NONNUMERIC)
         csv.writerow(['name', 'url', 'poem'])
         for lens in lenses:
             csv.writerow([lens['name'], lens['url'], lens['poem']])
