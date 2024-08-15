import json
import os


def print_towns(parent, output, print_village=True):
    if 'towns' in parent:
        town_types = ['街道', '镇', '乡']
        for town in parent['towns']:
            if any([town['name'].endswith(t) for t in town_types]) and town['name'].startswith(parent['name']):
                replaced = town['name'].replace(parent['name'], '', 1)
                if replaced in town_types:
                    output.write('\t' * 3 + town['name'] + '\n')
                else:
                    output.write('\t' * 3 + replaced + '\n')
            else:
                output.write('\t' * 3 + town['name'] + '\n')

            if print_village and 'villages' in town:
                strip_flag = True
                if 'villages' not in town:
                    print(parent['name'], town)
                if len(town['villages']) > 1:
                    for village in town['villages']:
                        if not village['name'].startswith(town['name']):
                            strip_flag = False
                            break
                else:
                    strip_flag = False

                for village in town['villages']:
                    if strip_flag:
                        output.write('\t' * 4 + village['name'].replace(town['name'], '', 1) + '\n')
                    else:
                        output.write('\t' * 4 + village['name'] + '\n')


def print_city(city, output, print_town=True, print_village=True):
    output.write('\t' + city['name'] + '\n')
    if 'counties' in city:
        for county in city['counties']:
            output.write('\t' * 2 + county['name'] + '\n')
            if print_town:
                print_towns(county, output, print_village)
    elif print_town and 'towns' in city:
        print_towns(city, output, print_village)


def print_all(year, codes, output, print_town=True):
    for _, province in sorted(codes):
        with open(os.path.join(year, province + '.json'), 'r', encoding='utf8') as file:
            data = json.load(file)
            output.write(province + '\n')
            for city in data['cities']:
                print_city(city, output, print_town, False)


def print_china(year):
    print(year)
    codes = []

    for path in os.listdir(year):
        if path.endswith('.json'):
            code = 0
            province = path[:path.index('.')]
            with open(os.path.join(year, path), 'r', encoding='utf8') as file:
                with open(os.path.join(year, province + '.txt'), 'w', encoding='utf8') as output:
                    data = json.load(file)
                    output.write(province + '\n')
                    for city in data['cities']:
                        if code == 0:
                            code = int(city['code'][0:2])
                            codes.append((code, province))
                        print_city(city, output)

    with open(os.path.join(year, '中国.txt'), 'w', encoding='utf8') as output:
        print_all(year, codes, output, False)

    with open(os.path.join(year, '中国城镇.txt'), 'w', encoding='utf8') as output:
        print_all(year, codes, output)


if __name__ == '__main__':
    for i in range(2009, 2024):
        print_china(str(i))
