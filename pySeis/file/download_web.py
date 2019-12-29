#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: yunnaidan
@time: 2019/11/22
@file: download_web.py
"""
import os
import requests


def data_select(
        home_url='http://service.ncedc.org',
        net='BK',
        sta='CMB',
        loc='00',
        cha='BHE',
        start='2011-11-26T09:31:00',
        end='2011-11-26T10:30:00',
        quality='B',
        minimumlength='0.0',
        longestonly='False',
        data_format='miniseed',
        out_path='.'):
    # Build data url.
    sub_url = '/fdsnws/dataselect/1/query?net={0}&sta={1}&loc={2}&cha={3}&start={4}&end={5}' \
              '&quality={6}&minimumlength={7}&longestonly={8}&format={9}&nodata=404'.format(
                net, sta, loc, cha, start, end, quality, minimumlength, longestonly, data_format)
    url = home_url + sub_url
    # Request the url.
    for times in range(10):
        r = requests.get(url)
        if r:
            break
    if not r:
        raise ValueError('Request error!')

    out_file=os.path.join(out_path,'.'.join([net,sta, cha, loc, start, end]+'.mseed'))
    with open(out_file, 'wb') as f:
        f.write(r.content)

    return None

if __name__ == '__main__':
    data_select()
    pass

