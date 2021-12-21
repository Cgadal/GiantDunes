"""
============
Figure 2
============

"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import calendar
from datetime import datetime, timedelta
import sys
import os
sys.path.append('../')
import python_codes.theme as theme


def tick_formatter(ax, fmt='%d'):
    myFmt = mdates.DateFormatter(fmt)
    ax.xaxis.set_major_formatter(myFmt)
    ticklabels = ax.get_xticklabels()
    ticklabels[0].set_ha('left')


# Loading figure theme
theme.load_style()

# path
path_imgs = '../static/images/'
path_savefig = '../Paper/Figures'
path_outputdata = '../static/output_data/data/'

# Loading wind data
Data = np.load(os.path.join(path_outputdata, 'Data_final.npy'), allow_pickle=True).item()
Stations = sorted(Data.keys())

# Figure properties
variables = ['U', 'Orientation']
label_var = {'U': r'Velocity, $u_{*}~[\textup{m}~\textup{s}^{-1}]$', 'Orientation': r'Orientation, $\theta~[^\circ]$'}
labels = [(r'\textbf{a}', r'\textbf{b}'), (r'\textbf{c}', r'\textbf{d}'), (r'\textbf{e}', r'\textbf{f}')]
row_labels = ['Huab station', 'Deep Sea station -- summer', 'Deep Sea station -- winter']
years = [2018, 2017, 2017]
months = [2, 12, 6]
days = [(11, 14), (5, 8), (1, 4)]
month_calendar = {index: month for index, month in enumerate(calendar.month_name) if month}


stations_plot = ['Huab_Station', 'Deep_Sea_Station', 'Deep_Sea_Station']

# #### Figure
fig = plt.figure(figsize=(theme.fig_width, 0.63*theme.fig_height_max), constrained_layout=True)
subfigs = fig.subfigures(nrows=3, ncols=1)
for i, (subfig, yr, mth, dy, station) in enumerate(zip(subfigs, years, months, days, stations_plot)):
    axarr = subfig.subplots(1, 2)
    subfig.suptitle(row_labels[i])
    subfig.set_facecolor('none')
    tmin = datetime(yr, mth, dy[0])
    tmax = datetime(yr, mth, dy[1])
    for j, (ax, var, label) in enumerate(zip(axarr, variables, labels[i])):
        l1, = ax.plot(Data[station]['time'], Data[station][var + '_station'], label='measurements', color=theme.color_insitu)
        l2, = ax.plot(Data[station]['time'], Data[station][var + '_era'], label='Era5Land', color=theme.color_Era5Land)
        ax.set_xlim(tmin, tmax)
        tick_formatter(ax)
        #
        # #### plot nights
        tstart = tmin - timedelta(days=1)
        tstart = tstart.replace(hour=10)
        x_night = [tstart + timedelta(days=i) for i in range((tmax-tmin).days + 2)]
        for daylight in x_night:
            a1 = ax.axvspan(daylight, daylight + timedelta(hours=12), facecolor=theme.color_day, alpha=0.1, edgecolor=None, label=theme.Icon_day)
            a2 = ax.axvspan(daylight - timedelta(hours=12), daylight, facecolor=theme.color_night, alpha=0.1, edgecolor=None, label=theme.Icon_night)
        #
        ax.set_ylabel(label_var[var])
        ax.set_xlabel('Days in {} {:d}'.format(month_calendar[tmin.month], tmin.year))
        ax.set_xticks([tmin + timedelta(days=i) for i in range((tmax-tmin).days + 1)])
        ax.text(0.02, 0.97, label, transform=ax.transAxes, ha='left', va='top')
        if var == 'U':
            ax.set_ylim((0, 9))
        else:
            ax.set_ylim((0, 360))
            ax.set_yticks((0, 90, 180, 270, 360))
#
# a1.set_edgecolor((0, 0, 0, 1))
first_legend = fig.legend(handles=[a1, a2], loc='center right', ncol=2, columnspacing=1, bbox_to_anchor=(1, 0.98), frameon=False)
#
plt.savefig(os.path.join(path_savefig, 'Figure2.pdf'),)
plt.show()
