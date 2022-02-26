import os

s_round = '2020-21_regular'
division = 'v1_w'
div_dir = '{0}/{1}'.format(s_round, division)

if not os.path.isdir(div_dir):
    os.makedirs(div_dir)
