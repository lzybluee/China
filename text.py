import json
import os

codes = []

for path in os.listdir():
    if path.endswith('.json'):
        code = 0
        province = path[:path.index('.')]
        with open(path, 'r', encoding='utf8') as file:
            with open(province + '.txt', 'w', encoding='utf8') as output:
                data = json.load(file)
                output.write(province + '\n')
                for city in data['cities']:
                    if code == 0:
                        code = int(city['code'][0:2])
                        codes.append((code, province))
                    output.write('\t' + city['name'] + '\n')
                    if 'counties' in city:
                        for county in city['counties']:
                            output.write('\t' * 2 + county['name'] + '\n')
                            if 'towns' in county:
                                for town in county['towns']:
                                    output.write('\t' * 3 + town['name'] + '\n')
                                    for village in town['villages']:
                                        output.write('\t' * 4 + village['name'] + '\n')
                    elif 'towns' in city:
                        for town in city['towns']:
                            output.write('\t' * 3 + town['name'] + '\n')
                            for village in town['villages']:
                                output.write('\t' * 4 + village['name'] + '\n')

with open('中国.txt', 'w', encoding='utf8') as output:
    for _, province in sorted(codes):
        with open(province + '.json', 'r', encoding='utf8') as file:
            data = json.load(file)
            output.write(province + '\n')
            for city in data['cities']:
                output.write('\t' + city['name'] + '\n')
                if 'counties' in city:
                    for county in city['counties']:
                        output.write('\t' * 2 + county['name'] + '\n')
                        if 'towns' in county:
                            for town in county['towns']:
                                output.write('\t' * 3 + town['name'] + '\n')
                elif 'towns' in city:
                    for town in city['towns']:
                        output.write('\t' * 3 + town['name'] + '\n')
