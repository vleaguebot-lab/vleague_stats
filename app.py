import glob
from pygments import highlight

import streamlit as st
import numpy as np
import pandas as pd
# import matplotlib.pyplot as plt
# from PIL import Image


def select_alg(df, jp_item, all_item, i):
    item_list = list(df[jp_item].unique())
    item_list.insert(0, all_item)
    select_item = columns[i].selectbox(
        '{}を選択'.format(jp_item),
        item_list
    )
    if select_item != all_item:
        df = df[df[jp_item] == select_item]
    return df, select_item


def metric_format(mean2, mean):
    if pd.isna(mean2):
        mean2f = '-'
        meanf = '-'
    else:
        mean2f = mean2
        meanf = (mean2-mean).round(2)
    return mean2f, meanf


st.title('Vリーグ成績公開サイト')
columns = st.columns(4)
columns[0].markdown('### *{}*'.format('by Vリーグbot'))

link = '[Vリーグ公式TOP](https://www.vleague.jp/record)'
link2 = '[公式記録・ランキング](https://www.vleague.jp/record)'
columns[-2].markdown(link, unsafe_allow_html=True)
columns[-1].markdown(link2, unsafe_allow_html=True)

columns = st.columns(2)
# ディビジョン選択
select_division = columns[0].selectbox(
    "ディビジョンを選択",
    ["V1男子", "V2男子", "V3男子", "V1女子", "V2女子"]
)
# 日本語からフォルダへ変更
rank = select_division[1]
if select_division[2:] == '男子':
    s_div = 'v{}_m'.format(rank)
elif select_division[2:] == '女子':
    s_div = 'v{}_w'.format(rank)

# データ選択
select_data = columns[1].selectbox(
    "データを選択",
    ["年間成績", "月別成績", "日別成績"]
)
# 日本語からフォルダへ変更
if select_data == "年間成績":
    s_data = 'yearly_all'
elif select_data == "月別成績":
    s_data = 'monthly_all'
elif select_data == "日別成績":
    s_data = 'daily_all'

file = '2021-22_regular/{0}/{1}.csv'.format(s_div, s_data)
df = pd.read_csv(file, encoding='cp932')
df_sum = df.iloc[:, 3:].sum()
len_df1 = len(df)

A_mean = (df_sum['アタック得点']/df_sum['アタック打数'])*100
BA_mean = (df_sum['バックアタック得点']/df_sum['バックアタック打数'])*100
BL_mean = df_sum['ブロック得点']/df_sum['出場数']
S_eff = (df_sum['サーブ得点']*100+df_sum['サーブ効果'] *
         25-df_sum['サーブ失点']*25)/df_sum['サーブ打数']
R_succ = (df_sum['サーブレシーブ成功・優']*100+df_sum['サーブレシーブ成功・良']*50)/df_sum['受数']

A_mean, BA_mean, BL_mean, S_eff, R_succ = A_mean.round(1), BA_mean.round(
    1), BL_mean.round(2), S_eff.round(2), R_succ.round(2)

st.markdown('### *{0} {1}*'.format(select_division, select_data))


# 月別成績のとき
columns = st.columns(3)
if select_data == '月別成績':
    df, select_month = select_alg(df, '年月', '全ての月', 0)

elif select_data == '日別成績':
    df, select_daily = select_alg(df, '試合日', '全ての日', 0)


# チーム選択
df, select_team = select_alg(df, 'チーム', '全チーム', 1)
# 選手選択
df, select_player = select_alg(df, '名前', '全選手', 2)

# if select_team != '全チーム' and select_player == '全選手':
#     BL_mean =

# グラフ作成

# 選択後の平均
df_sum = df.iloc[:, 3:].sum()
len_df2 = len(df)

A_mean2 = (df_sum['アタック得点']/df_sum['アタック打数'])*100
BA_mean2 = (df_sum['バックアタック得点']/df_sum['バックアタック打数'])*100
BL_mean2 = df_sum['ブロック得点']/df_sum['出場数']
S_eff2 = (df_sum['サーブ得点']*100+df_sum['サーブ効果'] *
          25-df_sum['サーブ失点']*25)/df_sum['サーブ打数']
R_succ2 = (df_sum['サーブレシーブ成功・優']*100+df_sum['サーブレシーブ成功・良']*50)/df_sum['受数']

if select_team != '全チーム' and select_player == '全選手':
    BL_mean2 = df_sum['ブロック得点'] / max(df['出場数'])

A_mean2, BA_mean2, BL_mean2, S_eff2, R_succ2 = A_mean2.round(
    1), BA_mean2.round(1), BL_mean2.round(2), S_eff2.round(2), R_succ2.round(2)


A_mean2f, A_meanf = metric_format(A_mean2, A_mean)
BA_mean2f, BA_meanf = metric_format(BA_mean2, BA_mean)
BL_mean2f, BL_meanf = metric_format(BL_mean2, BL_mean)
S_eff2f, S_efff = metric_format(S_eff2, S_eff)
R_succ2f, R_succf = metric_format(R_succ2, R_succ)


columns = st.columns(5)
if len_df1 > len_df2:
    st.markdown('##### *{}*'.format('全体平均との比較'))
    columns[0].metric('アタック決定率', '{}%'.format(
        A_mean2f), '{}%'.format(A_meanf))
    columns[1].metric('バックアタック決定率', '{}%'.format(
        BA_mean2f), '{}%'.format(BA_meanf))
    if select_player == '全選手':
        columns[2].metric('ブロック得点', '{}'.format(sum(df['ブロック得点'])))
    else:
        columns[2].metric('ブロックセット平均', '{}'.format(
            BL_mean2f), '{}'.format(BL_meanf))
    columns[3].metric('サーブ効果率', '{}%'.format(
        S_eff2f), '{}%'.format(S_efff))
    columns[4].metric('サーブレシーブ成功率', '{}%'.format(
        R_succ2f), '{}%'.format(R_succf))

ave = st.button('全体平均')
if ave:
    columns = st.columns(5)
    columns[0].metric('アタック決定率', '{0:.1f}%'.format(A_mean))
    columns[1].metric('バックアタック決定率', '{0:.1f}%'.format(BA_mean))
    if select_player != '全選手':
        columns[2].metric('ブロックセット平均', '{0:.2f}'.format(BL_mean))
    columns[3].metric('サーブ効果率', '{0:.1f}%'.format(S_eff))
    columns[4].metric('サーブレシーブ成功率', '{0:.1f}%'.format(R_succ))

chart_df = pd.DataFrame(
    {
        'アタック決定率': [A_mean, A_mean2],
        'バックアタック決定率': [BA_mean, BA_mean2],
        'ブロックセット平均': [BL_mean, BL_mean2],
        'サーブ効果率': [S_eff, S_eff2],
        'サーブレシーブ成功率': [R_succ, R_succ2]
    }
)

# arr = np.random.normal(1, 1, size=100)
# fig = plt.figure()

# for i in range(1, 4):
#     ax = fig.add_subplot(1, 3, i)
#     ax.hist(arr, bins=20)

# st.pyplot(fig)
highlight = st.button('ハイライトオフ')
if highlight:
    st.dataframe(df)
else:
    st.dataframe(df.style.highlight_max(axis=0))

if len_df1 > len_df2:
    columns = st.columns(3)

    columns[0].bar_chart(chart_df.iloc[:, 0], use_container_width=False)
    columns[1].bar_chart(chart_df.iloc[:, 1], use_container_width=False)
    columns[2].bar_chart(chart_df.iloc[:, 2], use_container_width=False)
    columns[0].bar_chart(chart_df.iloc[:, 3], use_container_width=False)
    columns[1].bar_chart(chart_df.iloc[:, 4], use_container_width=False)

    columns[2].write('左側: リーグ全体平均')
    columns[2].write('右側: 選択した選手・チームの成績')

    columns[2].dataframe(chart_df.T)
