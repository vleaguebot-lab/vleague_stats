import os
import datetime
import time
import re
import glob

import requests
import numpy as np
import pandas as pd

from bs4 import BeautifulSoup
import urllib.request as req


def stats_calc(df):
    df['アタック決定率'] = ((df['アタック得点'] / df['アタック打数']) * 100).round(1)
    df['アタック効果率'] = (((df['アタック得点']-df['アタック失点']) /
                     df['アタック打数']) * 100).round(1)
    df['バックアタック決定率'] = ((df['バックアタック得点'] / df['バックアタック打数']) * 100).round(1)
    df['アタックセット平均'] = (df['アタック得点'] / df['出場数']).round(2)
    df['ブロックセット平均'] = (df['ブロック得点'] / df['出場数']).round(2)
    df['サーブ効果率'] = ((df['サーブ得点'] * 100 + df['サーブ効果'] * 25 -
                    df['サーブ失点'] * 25) / df['サーブ打数']).round(1)
    df['サーブレシーブ成功率'] = (
        (df['サーブレシーブ成功・優'] * 100 + df['サーブレシーブ成功・良'] * 50) / df['受数']).round(1)
    return df


headers = {"User-Agent": "Mozilla/5.0"}

id_dict = {'v1_m': '318', 'v1_w': '317',
           'v2_m': '320', 'v2_w': '319', 'v3_m': '321'}
division = input('ディビジョン選択: ')
s_id = id_dict[division]

s_round = "2021-22_regular"
# os.chdir(s_round)

# if not os.path.isdir(division):
#     os.makedirs(division)


sets = ['1', '2', '3', '4', '5']
game_all = None

# レギュラーシーズン
url = 'https://www.vleague.jp/round/list/{}'.format(s_id)
print(url)
request = req.Request(url, headers=headers)
response = req.urlopen(request)
parse_html = BeautifulSoup(response, 'html.parser')

# ページ数取得
hrefs = parse_html.find_all('a', href=re.compile("pg"))
# print(hrefs)
if len(hrefs) > 0:
    pages = int(hrefs[-2].text)  # 後ろから2番目が最終ページを表す為(1番目は次のページ)
    print(pages)
else:
    pages = 1  # ページ数の無い場合は1ページ

all_list = []
url_list = []
for pg in range(1, pages+1):
    url = 'https://www.vleague.jp/round/list/{0}?pg={1}'.format(s_id, pg)
    print(url)
    request = req.Request(url, headers=headers)
    response = req.urlopen(request)
    parse_html = BeautifulSoup(response, 'html.parser')
    tables = parse_html.find_all('table')
    trs = tables[0].find_all('a', href=re.compile("/form/b"))
    for tr in trs:
        game_url = 'https://www.vleague.jp/' + tr.attrs['href']
        url_list.append(game_url)
print(url_list)

for url in url_list:
    # print(url)
    html = requests.get(url, headers=headers)
    check = html.text

    try:
        data = pd.read_html(check, header=[2])
    # 試合が無い場合は、以下の処理を飛ばす
    except:
        continue
    for j in range(2):
        stats = pd.DataFrame(data[j+4])
        stats = stats.rename(columns=str)
        col = stats.columns.values
        data_item = []
        for i in col:
            l = i
            data_item.append(l)
        for i in range(1, len(data_item)-2):
            data_item[-i] = data_item[-i-3]
            # print(data_item)
        for i in range(3):
            #     print(data_item[i])
            if data_item[i] == '出場数':
                data_item[i] = '背番号'
            elif data_item[i] == '1':
                data_item[i] = 'リベロ'
            else:
                data_item[i] = '名前'
        #     print(i, data_item[i])

        # カラム名変更
        new_stats = stats.rename(
            columns={col[i]: data_item[i] for i in range(len(data_item))})
        new_stats = new_stats.rename(columns={
            '打数': 'アタック打数', '得点': 'アタック得点', '失点': 'アタック失点', '決定率': 'アタック決定率',
            'セ平ット均': 'アタックセット平均', '打数.1': 'バックアタック打数', '得点.1': 'バックアタック得点',
            '失点.1': 'バックアタック失点', '決定率.1': 'バックアタック決定率', '得点.2': 'ブロック得点',
            'セ平ット均.1': 'ブロックセット平均', '打数.2': 'サーブ打数', '得点.3': 'サーブ得点', '失点.2': 'サーブ失点',
            '効果': 'サーブ効果', '効果率': 'サーブ効果率', '成功・優': 'サーブレシーブ成功・優',
            '成功・良': 'サーブレシーブ成功・良', '成功率': 'サーブレシーブ成功率'
        })

        request = req.Request(url, headers=headers)
        response = req.urlopen(request)
        parse_html = BeautifulSoup(response, 'html.parser')
        table_ha = parse_html.find_all('table')[0]
        td_ha = table_ha.find_all('td', class_='team')
        td_set = table_ha.find_all('td', class_='b')
        # print(td_ha)
        team = td_ha[j].text
        o_team = td_ha[-(j+1)].text
        print('team={}, o_team={}'.format(team, o_team))
        get_set = int(td_set[0].text)
        lost_set = int(td_set[-2].text)
        if j == 1:
            get_set, lost_set = lost_set, get_set
        print('get_set={}, lost_set={}'.format(get_set, lost_set))
        if get_set == 3:
            win_lose = 1
        else:
            win_lose = 0
        print('win_lose={}'.format(win_lose))

        new_stats['アタック決定率'] = (
            (new_stats['アタック得点'] / new_stats['アタック打数']) * 100).round(1)
        new_stats.insert(13, 'アタック効果率',
                         (((new_stats['アタック得点'] - new_stats['アタック失点']) / new_stats['アタック打数']) * 100).round(1))
        new_stats['総得点'] = new_stats['アタック得点'] + \
            new_stats['ブロック得点'] + new_stats['サーブ得点']
        span = parse_html.find_all('span')
        date = span[1].text.replace('/', '-')

        column_dict = {'勝敗': win_lose, '失セット': lost_set,
                       '得セット': get_set, '相手チーム': o_team, 'チーム': team, '試合日': date}
        for col, s in column_dict.items():
            new_stats.insert(0, col, s)

        # 名前のスペース(半角、全角)を削除
        new_stats['名前'] = new_stats['名前'].str.replace(
            '\u3000', '')
        new_stats['名前'] = new_stats['名前'].str.replace(' ', '')

        for by_set in sets:
            new_stats[by_set] = new_stats[by_set].astype(str)
        # 必要に応じてteamディレクトリを作成
        # team_dir = '{0}/{1}'.format(team,s_round)
        # if not os.path.isdir(team_dir):
        #     os.makedirs(team_dir)
        # new_stats.to_csv('{0}/{1}/{2}.csv'.format(team,s_round,date), index=False, encoding='cp932')
        print(new_stats)
        all_list.append(new_stats)
        # except:
        #     pass
print(all_list)
game_all = pd.concat(all_list, ignore_index=True)

# all_dir = 'all/{}'.format(s_round)

# if not os.path.isdir(all_dir):
# os.makedirs(all_dir)

print(os.getcwd())
# try:
daily_all = game_all[game_all['名前'] != 'チーム合計']
print(daily_all)
year_month = daily_all['試合日'].str[0:7]
daily_all.insert(1, '年月', year_month)
daily_all.set_index('試合日')
monthly_all = daily_all.groupby(
    ['名前', '年月', 'チーム', '背番号']).sum().reset_index()
monthly_all = stats_calc(monthly_all)
print(monthly_all)

yearly_all = daily_all.groupby(['名前', 'チーム', '背番号']).sum().reset_index()
yearly_all = stats_calc(yearly_all)
print(yearly_all)

div_dir = '{0}/{1}'.format(s_round, division)
game_all.to_csv('{}/game_all.csv'.format(div_dir),
                index=False, encoding='cp932')
daily_all.to_csv('{}/daily_all.csv'.format(div_dir),
                 index=False, encoding='cp932')
monthly_all.to_csv('{}/monthly_all.csv'.format(div_dir),
                   index=False, encoding='cp932')
yearly_all.to_csv('{}/yearly_all.csv'.format(div_dir),
                  index=False, encoding='cp932')
print('csv作成成功')
# except:
# print('cannot calculate')
# pass
