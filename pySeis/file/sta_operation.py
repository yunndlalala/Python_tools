"""
@version:
author:yunnaidan
@time: 2019/07/31
@file: sta_operation.py
@function:
"""
import os
import platform
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

LOCAL_PATH = '/Users/yunnaidan/Project/Dynamic_Triggering/Workspace/Central_California'
REMOTE_PATH = '/home/yunnd/Workspace/Dynamic_triggering/Central_California'
if platform.system() == 'Darwin':
    ROOT_PATH = LOCAL_PATH
if platform.system() == 'Linux':
    ROOT_PATH = REMOTE_PATH


def load_sta(sta_file, tar_chan):
    with open(sta_file, 'r') as f:
        data = f.readlines()
    sta_dic = {}
    for line in data[1:]:
        # print (line.split(','))
        net, sta, chan, _, _ = line.split(',')
        if chan == tar_chan:
            sta_dic['.'.join([net, sta, chan])] = []
    return sta_dic


def oper(data_path, sta_file, tar_chan='BHZ', outfile='sta_oper.txt'):
    sta_dic = load_sta(sta_file, tar_chan)
    for year in os.listdir(data_path):
        print (year)
        year_path = os.path.join(data_path, year)
        for day in os.listdir(year_path):
            print (day)
            day_path = os.path.join(year_path, day)
            # date = datetime.strptime(year + day[4:], '%Y%m%d')
            for mseed in os.listdir(day_path):
                # _, net, sta, chan, _ = mseed.split('.')
                net, sta, chan= mseed.split('.')
                sta_name = '.'.join([net, sta, chan])
                if sta_name in sta_dic.keys():
                    sta_dic[sta_name].append(day)
    if os.path.exists(outfile):
        os.remove(outfile)
    with open(outfile,'a') as f:
        for key in sta_dic.keys():
            f.writelines(key+','+','.join(sta_dic[key])+'\n')

    return None
def plot_oper(oper_file,outfile='sta_oper.png',show=True):
    plt.figure(figsize=[10,5])
    with open(oper_file,'r') as f:
        data=f.readlines()

    i = 1
    sta_name_list=[]
    for line in data:
        sta_name=line.split(',')[0]
        sta_name_list.append(sta_name.split('.')[1])
        value=line.split(',')[1:-1]
        value_date=[datetime.strptime(d, '%Y%m%d') for d in value]
        plt.scatter(sorted(value_date), [i] * len(value_date),s=1,marker='o')
        i+=1

    plt.yticks(range(1,i),sta_name_list)
    plt.xticks([datetime.strptime(str(s),'%Y') for s in range(2013,2020)],[str(s) for s in range(2013,2020)])
    # plt.xlim([datetime.strptime('2015','%Y'),datetime.strptime('20151230','%Y%m%d')])
    # plt.plot([datetime.strptime('20150501','%Y%m%d'),datetime.strptime('20150501','%Y%m%d')],[1,6],'--')
    plt.savefig(outfile)
    if show:
        plt.show()

    return None


if __name__ == '__main__':
    data_path = os.path.join(ROOT_PATH, 'data/time_series/raw_data/mseed')
    sta_file = os.path.join(
        ROOT_PATH,
        'data/station_info/stations_CI_selected_for_download_BH.txt')
    # oper(data_path, sta_file, tar_chan='BHZ')
    plot_oper('sta_oper.txt', outfile='sta_oper.png', show=True)
    print('Finish')
