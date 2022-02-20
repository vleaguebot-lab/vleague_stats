import streamlit as st
import numpy as np
import pandas as pd
# from PIL import Image
import glob

file = '2021-22_regular/yearly_all.csv'
df = pd.read_csv(file, encoding='cp932')

# 後で書き方直す
su = df.iloc[:, 3:].sum()
# su = df.sum(axis=1)

print(su)
