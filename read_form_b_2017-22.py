import time
import numpy as np
import pandas as pd
import os
import re
import datetime

# from dotenv import load_dotenv
from bs4 import BeautifulSoup
import urllib.request as req
import requests


def checkreplace(d):
    if d is not np.nan:
        return d.replace('　', '')
    else:
        return d


def create_db(division, s_id, s_round):
    # print(season)
    # game_id = get_game_id(division,season)
    headers = {"User-Agent": "Mozilla/5.0"}
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

    dbs = []
    teamdbs = []

    # カラム名
    columns = ['背番号', 'リベロ', '選手', '出場セット',
               '1', '2', '3', '4', '5',
               'アタック打数', 'アタック得点', 'アタック失点',
               'アタック決定率', 'アタック平均セット',
               'Bアタック打数', 'Bアタック得点', 'Bアタック失点', 'Bアタック決定率',
               'ブロック得点', 'ブロック平均セット', 'サーブ打数', 'サーブ得点',
               'サーブ失点', 'サーブ効果', 'サーブ効果率', 'サーブレシーブ受数',
               'サーブレシーブ成功・優', 'サーブレシーブ成功・良',
               'サーブレシーブ成功率']
    columns_e = ['No.', 'L', 'Player', 'Set', '1', '2', '3', '4', '5',
                 'AA', 'AP', 'AE', 'ASucc%', 'AP/S', 'BAA', 'BAP', 'BAE', 'BASucc%',
                 'BP', 'BP/S', 'SVA', 'SVP', 'SVE', 'SVx', 'SVEff%',
                 'RA', 'Rx', 'Rg', 'RSucc%']

    for url in url_list:
        time.sleep(1)
        # url_b = 'https://www.vleague.jp/form/b/' + g_id
        # print(url_b)

        # テキスト読み取り
        try:
            request = req.Request(url, headers=headers)
            response = req.urlopen(request)
            parse_html = BeautifulSoup(response, 'html.parser')
            check = parse_html.text
            match_num = parse_html.find(
                'p', class_='match_no left').find('span').text
        # 試合が無い場合は、以下の処理を飛ばす
        except:
            continue
        # if '試合データがありません' in check or '試合データの集計中です。しばらくお待ちください。' in check:
        #     continue
        # 試合番号

        # print(match_num)
        # 試合時間
        times = parse_html.find('div', class_='header2 cf').find_all('span')
        # print(times)
        spectators = times[1].text
        starttime = times[3].text
        endtime = times[5].text
        # totaltime = times[7].text
        jury = times[9].text.replace('　', '')
        chiefumpire = times[11].text.replace('　', '')
        subumpire = times[13].text.replace('　', '')
        judgeman = times[15].text.replace('　', '')
        # print(spectators,starttime,endtime,jury,chiefumpire,subumpire,judgeman)
        # 年月
        date = parse_html.find('p', class_='match_date left').find('span').text
        date = date.replace('/', '-')
        year = date[:4]
        month = date[5:7]
        day = date[-2:]
        # print(date,year,month,day)
        # 場所・会場
        place = parse_html.find(
            'p', class_='match_place left').find('span').text
        venue = parse_html.find('p', class_='venue').find('span').text
        # print(place,venue)

        # テーブル取得
        html = requests.get(url, headers=headers)
        check = html.text
        b_tables = pd.read_html(check)
        # b_tablesについて,0:得点・セット・時間, 1:スタメン背番号, 2:チーム監督・勝敗等, 3:評価, 4~5:各チーム個人成績
        scoretime = b_tables[0]
        hometeam = scoretime.loc[0, 'チーム']
        awayteam = scoretime.loc[1, 'チーム']
        # print(hometeam,awayteam)
        homeset = int(scoretime.loc[0, 'セット'])
        awayset = int(scoretime.loc[1, 'セット'])
        totalset = homeset + awayset
        # print(totalset)
        homewinlose = 'Win' if homeset >= 3 else 'Lose'
        awaywinlose = 'Lose' if homeset >= 3 else 'Win'
        # print(homewinlose,awaywinlose)
        homepoint = int(scoretime.loc[0, '合計'])
        awaypoint = int(scoretime.loc[1, '合計'])
        # print(homepoint,awaypoint)
        gametime = scoretime.loc[2, '合計']
        gametime = int(gametime[0])*60 + int(gametime[2:])
        # print(gametime)

        info = b_tables[2]
        homedirector = checkreplace(info.loc[0, 0])
        awaydirector = checkreplace(info.loc[0, 2])

        homecoach = checkreplace(info.loc[1, 0])
        awaycoach = checkreplace(info.loc[1, 2])
        # print(homedirector,homecoach,awaydirector,awaycoach)

        home = b_tables[4].copy()
        home.columns = columns_e
        home = home.iloc[1:, :]
        # ◯◯_jaは日本語
        home_ja = home.copy()
        home_ja.columns = columns
        # home_ja.to_csv('csv/{}/{}/{}-{}.csv'.format(division,season,date,hometeam),index=False)
        away = b_tables[5].copy()
        away.columns = columns_e
        away = away.iloc[1:, :]
        away_ja = away.copy()
        away_ja.columns = columns
        # away_ja.to_csv('csv/{}/{}/{}-{}.csv'.format(division,season,date,awayteam),index=False)
        # away.head()
        # print(len(home.columns), len(columns), len(columns_e))

        homedb = home.copy()
        homedb['Player'] = homedb['Player'].str.replace(' ', '')
        homedb['MatchNo.'], homedb['Date'] = match_num, date
        homedb['Year'], homedb['Month'], homedb['Day'] = year, month, day
        homedb['Place'], homedb['Venue'] = place, venue
        homedb['Team'], homedb['Op.Team'] = hometeam, awayteam
        homedb['Director'], homedb['Coach'] = homedirector, homecoach
        homedb['Win Set'], homedb['Lose Set'], homedb['Total Set'] = homeset, awayset, totalset
        homedb['Win Lose'], homedb['Get Point'], homedb['Lose Point'] = homewinlose, homepoint, awaypoint
        homedb['Game Time'], homedb['Start Time'], homedb['End Time'] = gametime, starttime, endtime
        homedb['Spectators'] = spectators
        homedb['Jury'], homedb['Chief Umpire'], homedb['Sub Umpire'], homedb['Judgeman'] = jury, chiefumpire, subumpire, judgeman
        homedb['Home Away'] = 'Home'
        hometeamdb = homedb.iloc[-1, 9:]
        homedb = homedb.iloc[:-1, :]
        awaydb = away.copy()
        awaydb['Player'] = awaydb['Player'].str.replace(' ', '')
        awaydb['MatchNo.'], awaydb['Date'] = match_num, date
        awaydb['Year'], awaydb['Month'], awaydb['Day'] = year, month, day
        awaydb['Place'], awaydb['Venue'] = place, venue
        awaydb['Team'], awaydb['Op.Team'] = awayteam, hometeam
        awaydb['Director'], awaydb['Coach'] = awaydirector, awaycoach
        awaydb['Win Set'], awaydb['Lose Set'], awaydb['Total Set'] = awayset, homeset, totalset
        awaydb['Win Lose'], awaydb['Get Point'], awaydb['Lose Point'] = awaywinlose, awaypoint, homepoint
        awaydb['Game Time'], awaydb['Start Time'], awaydb['End Time'] = gametime, starttime, endtime
        awaydb['Spectators'] = spectators
        awaydb['Jury'], awaydb['Chief Umpire'], awaydb['Sub Umpire'], awaydb['Judgeman'] = jury, chiefumpire, subumpire, judgeman
        awaydb['Home Away'] = 'Away'
        awayteamdb = awaydb.iloc[-1, 9:]
        awaydb = awaydb.iloc[:-1, :]
        # awaydb.tail()
        dbs.append(homedb)
        dbs.append(awaydb)

        homeOpdb = awayteamdb[:20].copy().rename(lambda x: 'Op'+x)
        # homeOpdb.head()
        awayOpdb = hometeamdb[:20].copy().rename(lambda x: 'Op'+x)
        # awayOpdb.head()
        hteamdb = pd.concat([hometeamdb, homeOpdb])
        ateamdb = pd.concat([awayteamdb, awayOpdb])
        teamdb = pd.concat([hteamdb, ateamdb], axis=1).T
        # teamdb.head()
        teamdbs.append(teamdb)

    # 個人成績を一括
    database = pd.concat(dbs)
    # チーム成績を一括
    teamdatabase = pd.concat(teamdbs)

    database.to_csv(
        'database/{1}/playerdb_{0}.csv'.format(s_round, division), index=False)
    teamdatabase.to_csv(
        'database/{1}/teamdb_{0}.csv'.format(s_round, division), index=False)


# load_dotenv()
# ディレクトリはC:\(自分の環境)\vleague
# os.chdir(os.environ['DIRECTORY'])

# division, season = input('Select division and season ').split()
# division = 'v2_m'
division = input('Select division: ')
# seasons = [str(x) for x in range(2020, 1999, -1)]
# seasons = ['2021']
# s_ids = ['']
# s_round = '2021-22_regular'
# s_id_dict = {'v1_m': '318', 'v2_m': '320',
#              'v3_m': '321', 'v1_w': '317', 'v2_w': '319'}
s_round = '2020-21_regular'
s_id_dict = {'v1_m': '301', 'v2_m': '299',
             'v3_m': '300', 'v1_w': '303', 'v2_w': '302'}
# s_round = '2019-20_regular'
# s_id_dict = {'v1_m': '283', 'v2_m': '288',
#              'v3_m': '287', 'v1_w': '277', 'v2_w': '281'}
# s_round = '2018-19_regular'
# s_id_dict = {'v1_m': '258', 'v2_m': '266',
#              'v3_m': '267', 'v1_w': '269', 'v2_w': '264'}
# s_round = '2017-18_regular'
# s_id_dict = {'v1_m': '241', 'v2_m': '247',
#              'v3_m': '250', 'v1_w': '243', 'v2_w': '248'}


s_id = s_id_dict[division]
# for s_id in s_ids:
#   try:
#     create_db(division,s_id)
#   except:
#     print('not exist {} season'.format(season))
#     pass

create_db(division, s_id, s_round)
