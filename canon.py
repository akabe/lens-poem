import requests
import csv
from bs4 import BeautifulSoup

def read(url):
    r = requests.get(url)
    r.encoding = r.apparent_encoding
    return BeautifulSoup(r.content, 'html.parser')

def parse_toppage(html):
    lenses = []
    for section in html.find_all('section', class_='box'):
        url = section.find('a')['href']
        name = ''.join(section.find('span', class_='name').strings)
        lenses.append({
            'name': name,
            'url': 'https://cweb.canon.jp' + url
        })
    return lenses

def parse_subpage(name, html):
    for div in html.find_all('div', class_='image'):
        alt = div.find('img')['alt']
        i = alt.find(name)
        if i == 0:
            return alt[len(name)+1:]
        elif i > 0:
            return alt[0:i]
    return None

if __name__ == '__main__':
    lenses = parse_toppage(read('https://cweb.canon.jp/ef/lineup/'))
    lenses.extend(parse_toppage(read('https://cweb.canon.jp/eos/rf/lineup/')))

    for lens in lenses:
        print(lens['name'])
        lens['poem'] = parse_subpage(lens['name'], read(lens['url']))

    with open('canon.csv', 'w') as fout:
         csv = csv.writer(fout, quoting=csv.QUOTE_NONNUMERIC)
         csv.writerow(['name', 'url', 'poem'])
         for lens in lenses:
             csv.writerow([lens['name'], lens['url'], lens['poem']])
