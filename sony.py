import requests
import csv
from bs4 import BeautifulSoup

def read(url):
    r = requests.get(url)
    r.encoding = r.apparent_encoding
    return BeautifulSoup(r.content, 'html.parser')

def parse_toppage(html):
    lenses = []
    for div in html.find_all('div', class_='s5-listItem4__main'):
        url = div.find('a')['href']
        name = ''.join(div.find('div', class_='s5-listItem4__description').strings).strip()
        lenses.append({
            'name': name,
            'url': 'https://www.sony.jp' + url
        })
    return lenses

def parse_subpage(html):
    lines = []
    div = html.find('div', class_='s5-featuresMisc1__body')
    if div is None:
        return None
    for li in div.find_all('li'):
        for s in li.strings:
            s = s.strip()
            if not (s in ['主な特長', 'レンズ構成図', '撮影例'] or s.find('防塵') != -1 or s.find('Teleconverter') != -1 or s.find('MTF') != -1) and s != '':
                lines.append(s)
    return '\n'.join(set(lines))

if __name__ == '__main__':
    lenses = parse_toppage(read('https://www.sony.jp/ichigan/lineup/e-lens.html'))
    lenses.extend(parse_toppage(read('https://www.sony.jp/ichigan/lineup/a-lens.html')))

    for lens in lenses:
        print(lens['name'])
        lens['poem'] = parse_subpage(read(lens['url']))

    with open('sony.csv', 'w') as fout:
         csv = csv.writer(fout, quoting=csv.QUOTE_NONNUMERIC)
         csv.writerow(['name', 'url', 'poem'])
         for lens in lenses:
             if lens['poem'] is not None:
                 csv.writerow([lens['name'], lens['url'], lens['poem'].replace('\n', '\\n')])
