"""
@version:
author:yunnaidan
@time: 2019/07/22
@file: download_mseed.py
@function:
"""
from obspy.clients.fdsn import Client
from obspy.core import UTCDateTime
import numpy as np
import obspy
import os
import re
import time
import glob
import shutil
import platform
import subprocess
import multiprocessing


def load_stations(filename):
    with open(filename, 'r') as f:
        sta_data = f.readlines()
    sta_list = []
    for l in range(1, len(sta_data)):
        sta_info = sta_data[l]
        net_name = re.split(',', sta_info)[0]
        sta_name = re.split(',', sta_info)[1]
        chan_name = re.split(',', sta_info)[2]
        sta_list.append([net_name, sta_name, chan_name])

    return sta_list


def set_folders(out_path, startday, endday):
    day = startday
    while day <= endday:
        year_folder = str(day.year).zfill(4)
        day_folder = str(day.year).zfill(
            4) + str(day.month).zfill(2) + str(day.day).zfill(2)
        out_folder = os.path.join(out_path, year_folder, day_folder)
        if not os.path.exists(out_folder):
            os.makedirs(out_folder)

        day = day + 86400

    return None


def obspy_download(
        client,
        net_name,
        sta_name,
        chn_name,
        starttime,
        endtime,
        out_path,
        time_thre=10):
    year_folder = str(starttime.year)
    day_folder = str(starttime.year).zfill(
        4) + str(starttime.month).zfill(2) + str(starttime.day).zfill(2)
    out_folder = os.path.join(out_path, year_folder, day_folder)

    outfile = os.path.join(
        out_folder, net_name + '.' + sta_name + '.' + chn_name + '.mseed')
    # Incremental download
    if not os.path.exists(outfile):
        t = 0
        flag = False
        while flag == False and t < time_thre:
            try:
                client.get_waveforms(
                    network=net_name,
                    station=sta_name,
                    location='--',
                    channel=chn_name,
                    starttime=starttime,
                    endtime=endtime,
                    filename=outfile)
                flag = True
            except BaseException:
                pass
            time.sleep(0.5)
            t += 1

        if not flag:
            with open('download.log', 'a') as f:
                f.write('No data: ' + outfile + '\n')

    return None


def obspy_download_parallel(
        data_center,
        startday,
        endday,
        sta_file,
        out_path,
        cores=1):

    set_folders(out_path, startday, endday)
    sta_list = load_stations(sta_file)

    with open('download.log', 'a') as f:
        f.write('>>> ' + str(time.localtime(time.time())) + '\n')
        f.write('The number of stations is: ' + str(len(sta_list)) + '\n')

    day = startday
    while day <= endday:
        t_b = time.time()
        with open('download.log', 'a') as f:
            f.write('Day: ' + str(day) + '\n')
        print(day)
        starttime = day
        endtime = day + 86400

        client = Client(data_center)

        if cores == 1:
            for i in range(len(sta_list)):
                sta = sta_list[i]
                print (sta)
                net_name = sta[0]
                sta_name = sta[1]
                chan_name = sta[2]
                obspy_download(
                    client,
                    net_name,
                    sta_name,
                    chan_name,
                    starttime,
                    endtime,
                    out_path)
        else:
            pass

        t_e = time.time()
        with open('download.log', 'a') as f:
            f.write('Using time: ' + str(t_e - t_b) + '\n')
        day = day + 86400

    return None


def stp_run_download(sta_list, download_date, out_path):
    with open('download.log', 'a') as f:
        f.write(str(download_date) + '\n')

    tb = time.time()
    year = str(download_date.year).zfill(4)
    month = str(download_date.month).zfill(2)
    day = str(download_date.day).zfill(2)
    day_folder = year + month + day
    out_folder = os.path.join(out_path, year, day_folder)

    out_folder_old = os.path.join(out_path + '_old', year, day_folder)

    p = subprocess.Popen(['stp'], stdin=subprocess.PIPE)
    s = "MSEED \n"

    for i in range(len(sta_list)):

        sta = sta_list[i]
        net_name = sta[0]
        sta_name = sta[1]
        chan_name = sta[2]

        out_sta_file = glob.glob(
            os.path.join(
                out_folder_old, '*%s.%s.%s*' %
                (net_name, sta_name, chan_name)))

        if len(out_sta_file) == 0:
            s += "WIN {} {} {} {}/{}/{},00:00:00 +1d \n".format(
                net_name, sta_name, chan_name, year, month, day)

    s += "quit \n"
    p.communicate(s.encode())

    out_files = glob.glob('%s%s%s*.*' % (year, month, day))
    for out_file in out_files:
        shutil.move(out_file, out_folder)

    te = time.time()
    with open('download.log', 'a') as f:
        f.write('Using time: ' + str(te - tb) + '\n')


def stp_download_parallel(startday, endday, sta_file, out_path, cores=1):
    '''

    :param startday: obspy.core.utcdatetime.UTCDateTime
    :param endday: obspy.core.utcdatetime.UTCDateTime
    :param sta_file: Network,Station,Channel,Latitude,Longitude
    :param out_path:
    :param cores:
    :return:
    '''
    if os.path.exists('download.log'):
        os.remove('download.log')
    with open('download.log', 'a') as f:
        f.write('>>> ' + str(time.localtime(time.time())) + '\n')

    set_folders(out_path, startday, endday)
    sta_list = load_stations(sta_file)

    pool = multiprocessing.Pool(processes=cores)
    tasks = []

    day = startday
    while day <= endday:
        print(day)
        # tasks.append((sta_list, day, out_path))
        stp_run_download(sta_list, day, out_path)
        day = day + 86400

    '''
    # chunksize is how many tasks will be processed by one processor
    rs = pool.starmap_async(stp_run_download, tasks, chunksize=1)
    # close() & join() is necessary
    # No more work
    pool.close()

    # simple progress bar
    while (True):
        remaining = rs._number_left
        print("finished:{0}/{1}".format(len(tasks) - remaining, len(tasks)),
              end='\r')  # '\r' means remove the last line
        if (rs.ready()):
            break
        time.sleep(0.5)

    # Wait for completion
    pool.join()
    '''

    return None


if __name__ == '__main__':
    LOCAL_PATH = '/Users/yunnaidan/Project/Dynamic_Triggering/Workspace/Central_California'
    REMOTE_PATH = '/home/yunnd/Workspace/Dynamic_triggering/Central_California'
    if platform.system() == 'Darwin':
        ROOT_PATH = LOCAL_PATH
    if platform.system() == 'Linux':
        ROOT_PATH = REMOTE_PATH

    startday = UTCDateTime('2009-01-03')
    endday = UTCDateTime('2009-01-05')

    sta_file = os.path.join(
        ROOT_PATH,
        'data/station_info/stations_CI_selected_for_download_BH.txt')

    out_path = os.path.join(ROOT_PATH, 'data/time_series/raw_data/mseed')
    data_center = 'SCEDC'
    obspy_download_parallel(
        data_center,
        startday,
        endday,
        sta_file,
        out_path,
        cores=1)
    # stp_download_parallel(startday, endday, sta_file, out_path, cores=15)

    pass
