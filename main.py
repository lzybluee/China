import json
import os
import re
import time
import traceback
from concurrent.futures import ThreadPoolExecutor

import requests


def get_html(url):
    html = None
    retry = False
    while html is None:
        try:
            respond = requests.get(url, timeout=30)
            if respond.status_code == 200:
                if b'utf-8' in respond.content:
                    html = respond.content.decode('utf8')
                else:
                    html = respond.content.decode('gb18030')
            else:
                print(url, 'Status code', respond.status_code)
        except Exception as e:
            print(url, e)
            retry = True
            time.sleep(30)
            continue

        if not html:
            print(url, 'No html!')
            retry = True
            time.sleep(30)
        elif '</table>' not in html:
            print(url, 'No html?', html)
            html = None
            retry = True
            time.sleep(30)
        elif retry:
            print(url, 'Retry success!')

    return html.replace("'", '"')


def get_villages(url):
    villages = []
    html = get_html(url)
    table = html[html.index('<table class='):html.index('</table>')]
    lines = table.split('<tr class="villagetr">')[1:]
    for line in lines:
        cells = re.findall('<td>(.*?)</td>', line)
        entries = [re.sub('<.*?>', '', cell) for cell in cells]
        villages.append({'name': entries[2], 'code': entries[0], 'type': entries[1]})
    return villages


def get_towns(url):
    towns = []
    html = get_html(url)
    table = html[html.index('<table class='):html.index('</table>')]
    lines = table.split('<tr class="towntr">')[1:]
    for line in lines:
        cells = re.findall('<td>(.*?)</td>', line)
        entries = [re.sub('<.*?>', '', cell) for cell in cells]
        town = {'name': entries[1], 'code': entries[0]}
        if href := re.findall('href="(.*?)"', line):
            if villages := get_villages(url[:url.rindex('/') + 1] + href[0]):
                town['villages'] = villages
        towns.append(town)
    return towns


def get_counties(url, city):
    counties = []
    html = get_html(url)
    table = html[html.index('<table class='):html.index('</table>')]
    lines = table.split('<tr class="countytr">')[1:]
    for line in lines:
        cells = re.findall('<td>(.*?)</td>', line)
        entries = [re.sub('<.*?>', '', cell) for cell in cells]
        county = {'name': entries[1], 'code': entries[0]}
        print(city + '-' + county['name'])
        if href := re.findall('href="(.*?)"', line):
            if towns := get_towns(url[:url.rindex('/') + 1] + href[0]):
                county['towns'] = towns
        counties.append(county)
    return counties


def get_cities(url, province):
    cities = []
    html = get_html(url)
    table = html[html.index('<table class='):html.index('</table>')]
    lines = table.split('<tr class="citytr">')[1:]
    for line in lines:
        cells = re.findall('<td>(.*?)</td>', line)
        entries = [re.sub('<.*?>', '', cell) for cell in cells]
        city = {'name': entries[1], 'code': entries[0]}
        if href := re.findall('href="(.*?)"', line):
            if counties := get_counties(url[:url.rindex('/') + 1] + href[0], province + '-' + city['name']):
                city['counties'] = counties
            else:
                print(province + '-' + city['name'])
                if towns := get_towns(url[:url.rindex('/') + 1] + href[0]):
                    city['towns'] = towns
        cities.append(city)
    return cities


def get_province(year, name, url):
    print('===', year, name, '===')
    try:
        if not os.path.exists(year):
            os.mkdir(year)

        database = {'name': name, 'cities': get_cities(url, name)}
        with open(os.path.join(year, name + '.json'), 'w', encoding='utf8') as file:
            json.dump(database, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print('Error!', name, e)
        traceback.print_exc()


def get_provinces(year, executor):
    url = 'https://www.stats.gov.cn/sj/tjbz/tjyqhdmhcxhfdm/' + year
    html = get_html(url)
    provinces = re.findall('<td.*?><a href="(.*?)">([^<]+)', html)

    for page, province in provinces:
        executor.submit(get_province, year, province, url + '/' + page)
        time.sleep(5)


def get_china():
    executor = ThreadPoolExecutor(8)

    for i in range(2009, 2024):
        get_provinces(str(i), executor)

    executor.shutdown()


if __name__ == '__main__':
    get_china()
