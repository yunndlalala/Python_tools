"""
@version:
author:yunnaidan
@time: 2019/07/21
@file: setup.py
@function:
"""
import os
from distutils.sysconfig import get_python_lib

# Set path
print ('>>> Set path...')

pwd=os.getcwd()
lib_path=get_python_lib()
pth_file=os.path.join(lib_path,'pySeis.pth')
with open(pth_file,'w') as f:
    f.write(pwd)