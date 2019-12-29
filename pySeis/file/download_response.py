"""
@version:
author:yunnaidan
@time: 2019/09/16
@file: download_response.py
@function:
"""
import os
import requests

def SCEDC_PZ(net, sta, cha, loc, start, end,out_path=''):
    home_url = 'http://service.scedc.caltech.edu'
    sub_url = '/scedcws/sacpz/1/query?net={0}&sta={1}&cha={2}&loc={3}&start={4}&end={5}&nodata=404'.format(
        net, sta, cha, loc, start, end)
    url=home_url+sub_url
    for times in range(10):
        r=requests.get(url)
        if r:
            break
    if not r:
        raise ValueError('Request error!')

    text=r.text
    lines=text.split('\n')

    node_index=[-1]
    for l_index,line in enumerate(lines):
        first_str=line.split(' ')[0]
        if first_str == 'CONSTANT':
            node_index.append(l_index)

    for i in range(len(node_index)-1):
        out_file=os.path.join(out_path,'.'.join([net, sta, cha, loc,str(i),'PZ']))
        with open(out_file,'w') as f:
            for l in range(node_index[i]+1,node_index[i+1]+1):
                f.writelines(lines[l]+'\n')
    return text

if __name__ == '__main__':
    out_path=''
    SCEDC_PZ('CI', 'ADO', 'BHN', '--', '2009-01-01T00:00:00', '2019-06-30T23:59:59',out_path)
    print ('Finish')
