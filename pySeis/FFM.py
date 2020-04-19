#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: yunnaidan
@time: 2020/01/08
@file: FFM.py
"""
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from pycpt.load import cmap_from_cptcity_url


class FFM(object):
    def __init__(self, FFM_data, row_n=12, column_n=21):
        """
        :param FFM_data: pandas.DataFrame with columns
        ['lon', 'lat', 'dep', 'lon1', 'lat1', 'dep1', 'lon2', 'lat2', 'dep2', 'lon3', 'lat3', 'dep3',
        'lon4', 'lat4', 'dep4', 'strike', 'dip', 'rake', 'slip_all']
        """
        self.FFM_df = FFM_data
        self.row_n = row_n
        self.column_n = column_n

    def get_dx_dy_map(self, slip, strike, dip, rake):
        strike_rad = np.deg2rad(strike)
        dip_rad = np.deg2rad(dip)
        rake_rad = np.deg2rad(rake)

        dx = np.cos(rake_rad) * np.sin(strike_rad) \
            - np.sin(rake_rad) * np.cos(dip_rad) * np.cos(strike_rad)
        dy = np.cos(rake_rad) * np.cos(strike_rad) \
            + np.sin(rake_rad) * np.cos(dip_rad) * np.sin(strike_rad)

        return slip * dx, slip * dy

    def plot_slip_2D_map(
            self,
            ax=None,
            zoom=1.0,
            point_color='k',
            arrow_color='k',
            point=False,
            patch=False,
            slip_patch=False,
            slip_arrow=False,
            arrow_width=0.001,
            outfile=None):
        # cmap = plt.cm.Paired
        cmap = cmap_from_cptcity_url('ncl/precip2_17lev.cpt')
        # norm = matplotlib.colors.Normalize(vmin=np.min(self.FFM_df['slip_all']), vmax=np.max(self.FFM_df['slip_all']))
        norm = matplotlib.colors.Normalize(vmin=0, vmax=10)

        if ax is None:
            fig = plt.figure()
            ax = fig.add_subplot(111)

        for row_i, row in self.FFM_df.iterrows():
            x = [
                row['lon1'],
                row['lon2'],
                row['lon3'],
                row['lon4'],
                row['lon1']]
            y = [
                row['lat1'],
                row['lat2'],
                row['lat3'],
                row['lat4'],
                row['lat1']]
            if patch:
                ax.plot(x, y, '-', color='gray', linewidth=0.5)
            if slip_patch:
                ax.plot(x, y, '-', color='gray', linewidth=0.5)
                ax.fill(x, y, color=cmap(norm(row['slip_all'])))

            arrow_b_x = row['lon']
            arrow_b_y = row['lat']
            if point:
                ax.plot(
                    arrow_b_x,
                    arrow_b_y,
                    '.',
                    color=point_color,
                    linewidth=0.1)
            if slip_arrow:
                slip = row['slip_all'] / zoom
                dx, dy = self.get_dx_dy_map(
                    slip, row['strike'], row['dip'], row['rake'])
                ax.arrow(
                    arrow_b_x,
                    arrow_b_y,
                    dx,
                    dy,
                    width=arrow_width,
                    color=arrow_color)

        ax.set_aspect('equal')

        if slip_patch:
            sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
            plt.colorbar(sm)

        if outfile is not None:
            plt.savefig(outfile)

        return ax

    def plot_stress_2D_map(
            self,
            stress=None,
            ax=None,
            slip_arrow=False,
            zoom=1.0,
            arrow_color='k',
            arrow_width=0.00001,
            outfile=None):
        if ax is None:
            fig = plt.figure()
            ax = fig.add_subplot(111)

        cmap = plt.cm.coolwarm
        bar_lim=np.max(abs(stress))
        norm = matplotlib.colors.Normalize(
            vmin=-bar_lim, vmax=bar_lim)

        for row_i, row in self.FFM_df.iterrows():
            x = [
                row['lon1'],
                row['lon2'],
                row['lon3'],
                row['lon4'],
                row['lon1']]
            y = [
                row['lat1'],
                row['lat2'],
                row['lat3'],
                row['lat4'],
                row['lat1']]

            ax.plot(x, y, '-', color='gray', linewidth=0.5)
            ax.fill(x, y, color=cmap(norm(stress[row_i])))

            if slip_arrow:
                arrow_b_x = row['lon']
                arrow_b_y = row['lat']
                slip = row['slip_all'] / zoom
                dx, dy = self.get_dx_dy_map(
                    slip, row['strike'], row['dip'], row['rake'])
                ax.arrow(
                    arrow_b_x,
                    arrow_b_y,
                    dx,
                    dy,
                    width=arrow_width,
                    color=arrow_color)

        ax.set_aspect('equal')
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        cbar = plt.colorbar(sm)
        cbar.formatter.set_powerlimits((0, 0))
        cbar.update_ticks()

        if outfile is not None:
            plt.savefig(outfile)

        return ax

    def get_dx_dy_plane(self, slip, rake):
        rake_rad = np.deg2rad(rake)
        x_direction = np.cos(rake_rad)
        y_direction = np.sin(rake_rad)

        return slip * x_direction, slip * y_direction

    def plot_shear_stress_plane(
            self,
            ax=None,
            strike_stresses=None,
            dip_stresses=None,
            zoom_stress=1.0,
            stress_color='gray',
            stress_label='',
            slip_bool=False,
            zoom_slip=1.0,
            slip_color='black',
            arrow_width=0.00001,
            outfile=None):
        if ax is None:
            fig = plt.figure()
            ax = fig.add_subplot(111)

        row_n = 21
        column_n = 12
        for row_i, row in self.FFM_df.iterrows():
            arrow_b_x = int((row_i+0.1)/column_n)
            arrow_b_y = 11 - row_i % column_n

            strike_stress=strike_stresses[row_i]/ zoom_stress
            dip_stress=dip_stresses[row_i]/ zoom_stress
            ax.arrow(
                arrow_b_x,
                arrow_b_y,
                strike_stress,
                -dip_stress,
                width=arrow_width,
                head_width=0.2,
                color=stress_color)

            if slip_bool:
                slip = row['slip_all'] / zoom_slip
                dx, dy = self.get_dx_dy_plane(slip, row['rake'])
                ax.arrow(
                    arrow_b_x,
                    arrow_b_y,
                    dx,
                    dy,
                    width=arrow_width,
                    head_width=0.2,
                    color=slip_color)

        ax.plot(arrow_b_x, arrow_b_y, stress_color, label=stress_label)
        if slip_bool:
            ax.plot(arrow_b_x, arrow_b_y, slip_color, label='slip')
        ax.set_xlim([-1, 21])
        ax.set_ylim([-1, 12])
        ax.set_aspect('equal')

        if outfile is not None:
            plt.savefig(outfile)

        return None

    def plot_shear_item_plane(
            self,
            ax=None,
            rake_bool=False,
            strike_item=None,
            dip_item=None,
            item=None,
            rake=None,
            zoom=1.0,
            color='gray',
            label='',
            line_width=0.00001,
            arrow_width=0.00001,
            outfile=None):
        if ax is None:
            fig = plt.figure()
            ax = fig.add_subplot(111)

        for row_i, row in self.FFM_df.iterrows():
            arrow_b_x = int((row_i+0.1)/self.row_n)
            arrow_b_y = self.row_n - 1 - row_i % self.row_n

            if rake_bool:
                item_value = item[row_i]
                rake_value = rake[row_i]
                item_value = item_value / zoom
                dx, dy = self.get_dx_dy_plane(item_value, rake_value)
                ax.arrow(
                    arrow_b_x,
                    arrow_b_y,
                    dx,
                    dy,
                    width=line_width,
                    head_width=arrow_width,
                    color=color)
            else:
                strike_item_i= strike_item[row_i] / zoom
                dip_item_i= dip_item[row_i] / zoom
                ax.arrow(
                    arrow_b_x,
                    arrow_b_y,
                    strike_item_i,
                    -dip_item_i,
                    width=line_width,
                    head_width=arrow_width,
                    color=color)

        ax.plot(arrow_b_x, arrow_b_y, color, label=label)
        ax.set_xlim([-1, 21])
        ax.set_ylim([-1, 12])
        ax.set_aspect('equal')

        if outfile is not None:
            plt.savefig(outfile)

        return ax