"""
@version:
author:yunnaidan
@time: 2019/09/19
@file: sac.py
@function:
"""
import os
import subprocess
import obspy
os.putenv("SAC_DISPLAY_COPYRIGHT", '0')


def lh(sacfile, head_name_lst):
    p = subprocess.Popen(
        ['sac'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE)
    s = "wild echo off \n"
    s += "rh %s \n" % (sacfile)
    s += "lh %s \n" % (' '.join(head_name_lst))
    s += "q \n"
    out, err = p.communicate(s.encode())
    out = out.decode().split('\n')
    header_lst=[line.split('=')[1][1:] for line in out[5:-1]]

    return header_lst, err



if __name__ == '__main__':
    sacfile = '20090101.CI.JRC2.BHZ'
    head_name_lst = ['nzyear','nzjday','nzhour','nzmin','nzsec','nzmsec']
    header_lst, _ = lh(sacfile, head_name_lst)
    print('Finish!')
