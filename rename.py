import os


def rename(year):
    renames = []

    for path in os.listdir(year):
        if path.endswith('.json'):
            name = path[:path.index('.')]
            if name in ['云南', '吉林', '四川', '安徽', '山东', '山西', '广东', '江苏', '江西', '河北', '河南', '浙江',
                        '海南', '湖北', '湖南', '甘肃', '福建', '贵州', '辽宁', '陕西', '青海', '黑龙江']:
                renames.append((path, name + '省' + '.json'))
            elif name in ['上海', '北京', '天津', '重庆']:
                renames.append((path, name + '市' + '.json'))
            elif name in ['内蒙古', '西藏']:
                renames.append((path, name + '自治区' + '.json'))
            elif name == '广西':
                renames.append((path, name + '壮族自治区' + '.json'))
            elif name == '宁夏':
                renames.append((path, name + '回族自治区' + '.json'))
            elif name == '新疆':
                renames.append((path, name + '维吾尔自治区' + '.json'))

    if renames:
        print(renames)

        for old, new in renames:
            os.renames(os.path.join(year, old), os.path.join(year, new))


if __name__ == '__main__':
    for i in range(2009, 2024):
        rename(str(i))
