#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: yunnaidan
@time: 2019/11/22
@file: seispider.py
"""
import re
import requests
# IncompleteRead error occur sometimes.
# A violent solution is as follows. (I haven't understand.)
# import httplib
# httplib.HTTPConnection._http_vsn = 10
# httplib.HTTPConnection._http_vsn_str = 'HTTP/1.0'


class FDSNWS(object):

    def __init__(self, home_url='http://service.iris.edu'):
        self.home_url = home_url

    def continuous_waveform(self,
                            net='IU',
                            sta='ANMO',
                            loc='00',
                            cha='BHZ',
                            start='2010-02-27T06:30:00.000',
                            end='2010-02-27T10:30:00.000',
                            quality='B',
                            minimumlength='0.0',
                            longestonly='False',
                            data_format='miniseed',
                            nodata='404',
                            out_file='example.mseed',
                            progress_bar=True):
        # Build data url.
        sub_url = '/fdsnws/dataselect/1/query?net={0}&sta={1}&loc={2}&cha={3}&start={4}&end={5}' \
                  '&quality={6}&minimumlength={7}&longestonly={8}&format={9}&nodata={10}'.format(
                      net, sta, loc, cha, start, end, quality, minimumlength, longestonly, data_format, nodata)
        url = self.home_url + sub_url

        # Request the url.
        for times in range(10):
            r = requests.get(url, stream=True)
            # Determine if the url is wrong or there is no target data.
            if r:
                break
        if not r:
            raise ValueError('Request error!')
        # total_length = int(r.headers('content-length'))

        # Download data
        with open(out_file, "wb") as f:
            chunk_n = 0
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    chunk_n += 1
                    if progress_bar:
                        print('\r Finished: %.1fMB' % (chunk_n/1024), end='')
                else:
                    raise ValueError('Chunk error!')
            print('\n')

        return None

        # TODO
        def event(self):
            pass


class IRISWS(object):

    def __init__(self):
        self.home_url = 'http://service.iris.edu'

    def sacpz(self,
              net='IU',
              sta='ANMO',
              cha='00',
              loc='BHZ',
              start='2010-02-27T06:30:00.000',
              end='2010-02-27T10:30:00.000',
              out_file='example.PZ'):
        sub_url = '/irisws/sacpz/1/query?net={0}&sta={1}&cha={2}&loc={3}&start={4}&end={5}'.format(
            net, sta, cha, loc, start, end)
        url = self.home_url + sub_url
        for times in range(10):
            r = requests.get(url)
            if r:
                break
        if not r:
            raise ValueError('Request error!')

        text = r.text
        lines = text.split('\n')

        node_index = [-1]
        for l_index, line in enumerate(lines):
            first_str = re.split('\s+', line)[0]
            if first_str == 'CONSTANT':
                node_index.append(l_index)

        for i in range(len(node_index) - 1):
            out_file_i = out_file + '_' + str(i)
            with open(out_file_i, 'w') as f:
                for l in range(node_index[i] + 1, node_index[i + 1] + 1):
                    f.writelines(lines[l] + '\n')
        return None


class SCEDCWS(object):
    def __init__(self):
        self.home_url = 'http://service.scedc.caltech.edu'

    def sacpz(self,
              net='CI',
              sta='ADO',
              loc='--',
              cha='BHN',
              start='2009-01-01T00:00:00',
              end='2019-06-30T23:59:59',
              out_file='example.pz',
              nodata='404'):
        sub_url = '/scedcws/sacpz/1/query?net={0}&sta={1}&cha={2}&loc={3}&start={4}&end={5}&nodata={6}'.format(
            net, sta, cha, loc, start, end, nodata)
        url = self.home_url + sub_url
        for times in range(10):
            r = requests.get(url)
            if r:
                break
        if not r:
            raise ValueError('Request error!')

        text = r.text
        lines = text.split('\n')

        node_index = [-1]
        for l_index, line in enumerate(lines):
            first_str = re.split('\s+', line)[0]
            if first_str == 'CONSTANT':
                node_index.append(l_index)

        for i in range(len(node_index) - 1):
            out_file_i = out_file + '_' + str(i)
            with open(out_file_i, 'w') as f:
                for l in range(node_index[i] + 1, node_index[i + 1] + 1):
                    f.writelines(lines[l] + '\n')
        return None