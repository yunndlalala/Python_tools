"""
@version:
author:yunnaidan
@time: 2019/10/17
@file: waveform.py
@function:
"""
import os
import glob
import logging
import subprocess
from obspy.core import *

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

os.putenv("SAC_DISPLAY_COPYRIGHT", '0')


def _sac_error(out):
    for o in out:
        if "ERROR" in o:
            raise ValueError(o)

    return None


def cut(
        data_path=None,
        output_path=None,
        catalog_file=None):
    """
        input:
        catalog; stream_path; out_path; time window
        output:
        ./events/[origin time]/net.sta.ot.chn.SAC
        head file:
        stlo stla stel
        evlo evla evdp
        kztime
        b = 0
        other:
        The structure of data storage must be [year]/[yearmonthday]/sac file
        The catalog must be
                            time,latitude,longitude,depth,mag
                            Y-m-dTH:M:SZ,lat,lon,depth,mag
                            .............................
                            .............................
    """
    if os.path.exists(output_path):
        os.system('rm -rf %s' % output_path)
    else:
        os.makedirs(output_path)

    with open(catalog_file, 'r') as f:
        catalog = f.readlines()

    for ctlg_line in catalog[1:]:
        print('cutting event {}'.format(ctlg_line))
        ot, lat, lon, depth, mag, win_before, win_after = ctlg_line[:-1].split(',')

        win_before = float(win_before)
        win_after = float(win_after)
        ot = UTCDateTime(ot)

        # make output dir
        time_key = ''.join(['%04d' %
                            ot.year, '%02d' %
                            ot.month, '%02d' %
                            ot.day, '%02d' %
                            ot.hour, '%02d' %
                            ot.minute, '%02d' %
                            ot.second, '%03d' %
                            (ot.microsecond / 1000)])
        output_event_dir = os.path.join(output_path, time_key)
        if not os.path.exists(output_event_dir):
            os.makedirs(output_event_dir)

        # time window for slicing
        ts = ot - win_before
        ts_date_str = '%04d' % ts.year + '%02d' % ts.month + '%02d' % ts.day
        te = ot + win_after
        te_date_str = '%04d' % te.year + '%02d' % te.month + '%02d' % te.day

        start_day_path = os.path.join(data_path, str(ts.year), ts_date_str)
        # use sac
        if os.path.exists(start_day_path):
            os.chdir(start_day_path)
            streams = sorted(glob.glob('*'))
            for stream in streams:
                print(stream)
                _, net, sta, chn = stream.split('.')
                fname = '.'.join([net, sta, chn])
                output_file = os.path.join(output_event_dir, fname)

                b = ts - UTCDateTime(ts_date_str)
                e = te - UTCDateTime(ts_date_str)

                # cut event and change the head file
                long_stream_flag = False
                if te.day != ts.day:
                    next_stream = os.path.join(data_path, str(
                        te.year), te_date_str, '.'.join([te_date_str, net, sta, chn]))
                    if os.path.exists(next_stream):
                        long_stream_flag = True

                        p = subprocess.Popen(
                            ['sac'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
                        s = "wild echo off \n"
                        s += "r %s \n" % os.path.join(start_day_path, stream)
                        s += "merge GAP ZERO o a %s \n" % next_stream
                        s += "w %s \n" % (os.path.join(start_day_path,
                                                       'long.' + stream))
                        s += "q \n"
                        out, err = p.communicate(s.encode())
                        out = out.decode().split('\n')
                        print('SAC out: ' + str(out))
                        _sac_error(out)

                        stream = 'long.' + stream
                    else:
                        logging.warning('The data of next day is not found!')

                p = subprocess.Popen(
                    ['sac'],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE)
                s = "wild echo off \n"
                s += "cuterr fillz \n"
                s += "cut b %s %s \n" % (b, e)
                s += "r %s \n" % os.path.join(start_day_path, stream)
                s += "ch LCALDA TRUE \n"
                s += "ch LOVROK TRUE \n"
                s += "ch nzyear %s nzjday %s \n" % (
                    str(ot.year), str(ot.julday))
                s += "ch nzhour %s nzmin %s nzsec %s \n" % (
                    str(ot.hour), str(ot.minute), str(ot.second))
                s += "ch nzmsec %s \n" % str(ot.microsecond / 1000)
                # Otherwise it will report warning:reference time is not equal
                # to zero.
                s += "ch iztype IO \n"
                # b is not needed to be modified.
                s += "ch b %s \n" % str(-win_before)
                s += "ch evlo %s evla %s evdp %s \n" % (lon, lat, depth)
                s += "ch mag %s \n" % mag
                s += "w %s \n" % output_file
                s += "q \n"
                out, err = p.communicate(s.encode())
                out = out.decode().split('\n')
                print('SAC out: ' + str(out))
                _sac_error(out)

                if long_stream_flag:
                    print('remove ' + os.path.join(start_day_path, stream))
                    os.system('rm %s' % os.path.join(start_day_path, stream))
        else:
            logging.warning('%s is not exist!' % str(ot))
