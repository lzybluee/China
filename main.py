import json
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
                html = respond.content.decode('utf8')
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

    return html


def get_villages(url):
    villages = []
    html = get_html(url)
    table = html[html.index('<table class="villagetable">'):html.index('</table>')]
    lines = table.split('<tr class="villagetr">')[1:]
    for line in lines:
        cells = re.findall('<td>(.*?)</td>', line)
        entries = [re.sub('<.*?>', '', cell) for cell in cells]
        villages.append({'name': entries[2], 'code': entries[0], 'type': entries[1]})
    return villages


def get_towns(url, from_county=True):
    towns = []
    html = get_html(url)
    if from_county:
        table = html[html.index('<table class="towntable">'):html.index('</table>')]
    else:
        table = html[html.index('<table class="countytable">'):html.index('</table>')]
    lines = table.split('<tr class="towntr">')[1:]
    for line in lines:
        cells = re.findall('<td>(.*?)</td>', line)
        entries = [re.sub('<.*?>', '', cell) for cell in cells]
        town = {'name': entries[1], 'code': entries[0]}
        if href := re.findall('href="(.*?)"', line):
            town['villages'] = get_villages(url[:url.rindex('/') + 1] + href[0])
        towns.append(town)
    return towns


def get_counties(url, city):
    counties = []
    html = get_html(url)
    table = html[html.index('<table class="countytable">'):html.index('</table>')]
    lines = table.split('<tr class="countytr">')[1:]
    for line in lines:
        cells = re.findall('<td>(.*?)</td>', line)
        entries = [re.sub('<.*?>', '', cell) for cell in cells]
        county = {'name': entries[1], 'code': entries[0]}
        print(city + '-' + county['name'])
        if href := re.findall('href="(.*?)"', line):
            county['towns'] = get_towns(url[:url.rindex('/') + 1] + href[0])
        counties.append(county)
    return counties


def get_cities(url, province):
    cities = []
    html = get_html(url)
    table = html[html.index('<table class="citytable">'):html.index('</table>')]
    lines = table.split('<tr class="citytr">')[1:]
    for line in lines:
        cells = re.findall('<td>(.*?)</td>', line)
        entries = [re.sub('<.*?>', '', cell) for cell in cells]
        city = {'name': entries[1], 'code': entries[0]}
        if href := re.findall('href="(.*?)"', line):
            counties = get_counties(url[:url.rindex('/') + 1] + href[0], province + '-' + city['name'])
            if counties:
                city['counties'] = counties
            else:
                print(province + '-' + city['name'])
                city['towns'] = get_towns(url[:url.rindex('/') + 1] + href[0], False)
        cities.append(city)
    return cities


def get_province(name, url):
    print('===' + name + '===')
    try:
        database = {'name': name, 'cities': get_cities(url, name)}
        with open(name + '.json', 'w', encoding='utf8') as file:
            json.dump(database, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print('Error!', name, e)
        traceback.print_exc()


def get_provinces(url):
    html = get_html(url)
    provinces = re.findall('<td><a href="(.*?)">(.*?)<br />', html)

    pool = ThreadPoolExecutor(8)
    for page, province in provinces:
        pool.submit(get_province, province, url + page)
        time.sleep(5)


if __name__ == '__main__':
    get_provinces('https://www.stats.gov.cn/sj/tjbz/tjyqhdmhcxhfdm/2023/')
