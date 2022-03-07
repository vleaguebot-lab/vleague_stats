import os
import datetime
import time
import re
import glob

import requests
import numpy as np
import pandas as pd


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


division = input('ディビジョン選択: ')

season = '2021-22_regular'
yearly_path = '{0}/{1}/yearly_all.csv'.format(season, division)
yearly_all = pd.read_csv(yearly_path, encoding='cp932')
print(yearly_all.head())
