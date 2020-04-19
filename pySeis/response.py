#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: yunnaidan
@time: 2020/02/15
@file: response.py
"""
import re
import numpy as np
import matplotlib.pyplot as plt


def load_gf(PZ_file):
    with open(PZ_file, 'r') as f:
        text = f.readlines()

    type_line = text[21]
    type = type_line.split(':')[1].split('(')[1].split(')')[0]

    sensitivity_line = text[21]
    sensitivity = float(sensitivity_line.split(':')[1].split('(')[0])
    normalizing_line = text[22]
    normalizing = float(normalizing_line.split(':')[1][:-1])

    zero_no = int(re.split('\s+', text[24])[1])
    zeros = []
    for i in range(zero_no):
        zero_info = text[25 + i]
        _, real, im = re.split('\s+', zero_info[:-1])
        zeros.append(complex(float(real), float(im)))

    # Delete zero points equalling to zero according to the data type.
    if type == 'M/S':
        zeros.remove(0.0)
    if type == 'M/S**2':
        zeros.remove(0.0)
        zeros.remove(0.0)

    pole_line_index = 24 + zero_no + 1
    pole_no = int(re.split('\s+', text[pole_line_index])[1])
    poles = []
    for i in range(pole_no):
        pole_info = text[pole_line_index + 1 + i]
        _, real, im = re.split('\s+', pole_info[:-1])
        poles.append(complex(float(real), float(im)))

    return type, sensitivity, normalizing, zeros, poles


def gf(sensitivity, normalizing, zeros, poles, f):
    s = complex(0, 2 * np.pi * f)
    gf1 = 1
    for zero in zeros:
        gf1 = gf1 * (s - zero)
    gf2 = 1
    for pole in poles:
        gf2 = gf2 * (s - pole)
    gf = sensitivity * normalizing * gf1 / gf2

    return abs(gf)


def plot_gf(
        gf_file,
        frequencies=np.arange(
            0.01,
            20,
            0.0001),
    ax=None,
        **plt_paras):
    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(111)

    type, sensitivity, normalizing, zeros, poles = load_gf(gf_file)
    gf_list = np.array(
        [gf(sensitivity, normalizing, zeros, poles, f) for f in frequencies])

    ax.plot(frequencies, gf_list, **plt_paras)
    ax.set_yscale('log')
    ax.set_xscale('log')
    ax.set_xlabel('Frequency ' + '$\mathregular{(Hz)}$')
    ax.set_ylabel('Count/' + type)

    return ax


if __name__ == '__main__':
    gf_file = '/Users/yunnaidan/Project/Dynamic_triggering/Changning/data/PZ/SC.XWE.BHZ.txt'
    # gf_file = '/Users/yunnaidan/OneDrive - pku.edu.cn/Notes/station_response/response_files/IU.COLA.00.BHZ.v.PZ.txt'
    frequencies = np.arange(0.001, 100, 0.0001)
    ax = plot_gf(gf_file, frequencies=frequencies, color='r')
    plt.show()

    pass
