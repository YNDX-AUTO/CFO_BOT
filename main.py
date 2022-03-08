import copy
import datetime
from datetime import timedelta
from bs4 import BeautifulSoup as bs
import requests
import re
import time
from dotenv import load_dotenv
import os


load_dotenv()

TOKEN = os.getenv('TOKEN')
CHAT_ID = os.getenv('CHAT')
RG = ['lipetskaya_oblast', 'belgorodskaya_oblast', 'ivanovskaya_oblast', 'tulskaya_oblast', 'smolenskaya_oblast',
      'tverskaya_oblast', 'orlovskaya_oblast', 'bryanskaya_oblast', 'kaluzhskaya_oblast', 'ryazanskaya_oblast',
      'kostromskaya_oblast', 'tambovskaya_oblast', 'kurskaya_oblast', 'vladimirskaya_oblast', 'yaroslavskaya_oblast']
REGIONS = {'lipetskaya_oblast': None,
           'tambovskaya_oblast': None,
           'belgorodskaya_oblast': None,
           'smolenskaya_oblast': None,
           'orlovskaya_oblast': None,
           'bryanskaya_oblast': None,
           'kurskaya_oblast': None,
           'ivanovskaya_oblast': None,
           'vladimirskaya_oblast': None,
           'kostromskaya_oblast': None,
           'yaroslavskaya_oblast': None,
           'tulskaya_oblast': None,
           'ryazanskaya_oblast': None,
           'kaluzhskaya_oblast': None,
           'tverskaya_oblast': None,
           }
day_base = {'base': None}

URL = 'https://auto.ru/lipetskaya_oblast/cars/used/?seller_group=COMMERCIAL'
URL_BEGIN = 'https://auto.ru/'
URL_END = '/cars/used/?seller_group=COMMERCIAL'
HEADERS = {'accept': '*/*', 'user-agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) '
                                         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 '
                                         'Mobile Safari/537.36'}


def main() -> str:
    copy_base = copy.deepcopy(REGIONS)
    copy_day_base = copy.deepcopy(day_base)
    for geo in RG:
        print(geo)
        url = URL_BEGIN + geo + URL_END
        print(url)
        r = requests.get(url, HEADERS).text
        soup = bs(r, 'html.parser')
        print(soup)
        try:
            print('exit')
            count = soup.find('span', class_='ButtonWithLoader__content')
            print(count)
            count = soup.find('span', class_='ButtonWithLoader__content').text
            print(count)
            numb = re.sub('\D', '', count)
            print(geo, numb)
            REGIONS[geo] = int(numb)
        except AttributeError:
            print(f'{geo} not accessable')
        time.sleep(14)
    all_base_count = [x for x in list(REGIONS.values()) if x is not None]
    sum_base_count = sum(all_base_count)
    day_base['base'] = sum_base_count
    try:
        diff_in_total_base = day_base['base'] - copy_day_base['base']
    except TypeError:
        diff_in_total_base = 0
    regions_with_max_dif = count_diff_for_regions(copy_base, REGIONS)
    if regions_with_max_dif:
        message_info = f'База ЦФО: {sum_base_count} ({diff_in_total_base})\n' \
                       f'{regions_with_max_dif}'
        return message_info
    return f'База ЦФО: {sum_base_count} ({diff_in_total_base})'


def count_diff_for_regions(copy: dict, last_dict: dict) -> str:
    text = ''
    for geo in last_dict:
        try:
            absolut_diff = copy[geo] - last_dict[geo]
            dif = (absolut_diff/last_dict[geo]*100)
            if dif > 10:
                signal_attention = f'{geo} +{absolut_diff}'
                text += signal_attention + '\n'
            elif dif < -10:
                signal_attention = f'{geo} {absolut_diff}'
                text += signal_attention + '\n'
            else:
                pass
        except TypeError:
            pass
    return text


def message_bot() -> None:
    value = main()
    URL_BOT = ('https://api.telegram.org/bot{token}/sendMessage'.format(token=TOKEN))
    data = {'chat_id': CHAT_ID,
            'text': value
            }
    requests.post(URL_BOT, data=data)


if __name__ == '__main__':
    while True:
        time_now = datetime.datetime.now() + timedelta(hours=3)
        h = time_now.hour
        m = time_now.minute
        d = time_now.date().strftime("%d")
        print(f'check time {h}:{m}')
        if m in range(0, 30) and h == 8 or m in range(0, 59) and h == 18:
            print(f'start script {d}-{h}:{m}')
            message_bot()
            time.sleep(32400)
        else:
            time.sleep(1200)
