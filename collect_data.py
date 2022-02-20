import os
import datetime
import time
import re
import glob

import requests
import numpy as np
import pandas as pd

# from bs4 import BeautifulSoup
# import urllib.request as req

headers = {"User-Agent": "Mozilla/5.0"}

id_dict = {'v1_m': '318', 'v1_w': '317',
           'v2_m': '320', 'v2_w': '319', 'v3_m': '321'}
division = input('ディビジョン選択: ')
id = id_dict[division]

s_round = "2021-22_regular"

os.chdir(s_round)

if not os.path.isdir(division):
    os.makedirs(division)

df =
