"""
@version:
author:yunnaidan
@time: 2019/07/21
@file: process_seed.py
@function:
"""
import os
import time
import obspy
import subprocess

def rdseed_batch(mseed_file_dir,out_file_dir,PZ=False,RES=False):
    if PZ==True and RES==True:
        raise ValueError("'PZ' and 'RES' cannot both be True")

    for mseed_file in os.listdir(mseed_file_dir):
        if PZ==False and RES==False:
            os.system('rdseed -pdf ')
    return None
def mseed2sac_batch(mseed_file_dir,out_file_dir):
    os.chdir(out_file_dir)
    for root,dirs,files in os.walk(mseed_file_dir):
        for mseed_file in files:
            #print (os.path.join(root,mseed_file))
            os.system('mseed2sac %s'%os.path.join(root,mseed_file))

    return None

def load_sta(sta_file,tar_chan='BHZ'):
    with open(sta_file, 'r') as f:
        data = f.readlines()
    sta_dic = {}
    for line in data[1:]:
        net, sta, chan, lat, lon = line[:-1].split(',')
        if chan == tar_chan:
            sta_dic['.'.join([net, sta])] = [lon,lat]
    return sta_dic


def write_batch(mseed_file_dir,out_file_dir,sta_file,year_list,info_file=None):
    # if info_file != None:
    #     if os.path.exists(info_file):
    #         os.remove(info_file)
    # start=time.time()
    sta_dic=load_sta(sta_file)
    for year in year_list:
        print (year)
        year_path=os.path.join(mseed_file_dir,year)
        for day in sorted(os.listdir(year_path)):
            # day='20090813'
            print (day)
            day_path=os.path.join(year_path,day)
            out_path = os.path.join(out_file_dir, year, day)
            if not os.path.exists(out_path):
                os.makedirs(out_path)
            for mseed_file in sorted(os.listdir(day_path)):
                # start=time.time()
                print (mseed_file)
                _,net,sta,chan,_=mseed_file.split('.')
                out_file = os.path.join(out_path, '.'.join([day,net,sta,chan]))
                if os.path.exists(out_file):
                    continue

                mseed_file_path=os.path.join(day_path,mseed_file)
                st=obspy.read(mseed_file_path)
                mseed_count=len(st)
                print ('Mseed files: %i'%mseed_count)
                st_new=st.merge(fill_value=0)
                tr=st_new[0]
                sr = tr.stats.sampling_rate
                tr.write(out_file,format="SAC")

                # modify head info
                os.chdir(out_path)
                sac_file='.'.join([day,net,sta,chan])
                lon=sta_dic['.'.join([net,sta])][0]
                lat = sta_dic['.'.join([net, sta])][1]
                p = subprocess.Popen(['sac'], stdin=subprocess.PIPE)
                s = "wild echo off \n"
                s += "r %s \n" % (sac_file)
                s += "ch stlo %s stla %s \n" % (lon, lat)
                s += "wh \n"
                s += "q \n"
                p.communicate(s.encode())
                if info_file != None:
                    with open(info_file,'a') as f:
                        f.writelines(mseed_file+': %sHz, %s files\n'%(str(sr),str(mseed_count)))
                # end = time.time()
                # print (end-start)
    # end=time.time()
    # print (end-start)
    return None

if __name__ == '__main__':
    mseed_file_dir='/Users/yunnaidan/Project/Dynamic_Triggering/Workspace/Central_California/data/time_series/raw_data/mseed'
    out_file_dir='/Users/yunnaidan/Project/Dynamic_Triggering/Workspace/Central_California/data/time_series/raw_data/sac'
    sta_file='/Users/yunnaidan/Project/Dynamic_Triggering/Workspace/Central_California/data/station_info/stations_CI_selected_for_download_BH.txt'
    year_list=['2009']
    PZ=True
    RES=False
    #mseed2sac_batch(mseed_file_dir, out_file_dir)
    write_batch(mseed_file_dir, out_file_dir,sta_file,year_list)
    # mseed2sac_batch(mseed_file_dir,out_file_dir,PZ=PZ,RES=RES)
    print ('Finish')