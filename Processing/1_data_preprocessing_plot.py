"""
==============================
Preprocessing of the wind data
==============================

For each station, we follow these preprocessing steps:

    - put the wind direction in the trigonometric referential (counter clockwise, 0 in the WE-direction).
    - averaging of the in situ data in 1-hr bins centered on the time stamps of the Era5Land dataset.
    - filtering unusued data (NaNs, 0 velocity)


"""


import os
import sys
import glob
import numpy as np
from scipy.stats import binned_statistic
from datetime import datetime, timedelta
sys.path.append('../')
from python_codes.general import cosd, sind
import python_codes.theme as theme
#
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

theme.load_style()

Names = {
        'u10': '10 metre U wind component',
        'v10': '10 metre V wind component',
        'blh': 'Boundary layer height',
        't': 'Temperature',
        'q': 'Specific humidity',
        'z': 'Geopotential',
        'levels': 'Pressure levels'
        }

# paths
path_outputdata = '../static/data/processed_data/'
path_inputdata = '../static/data/raw_data'

Stations = ['Adamax_Station', 'Deep_Sea_Station', 'Huab_Station', 'South_Namib_Station']

list_file_ERA5Land = glob.glob(os.path.join(path_inputdata, 'ERA5Land/*.npy'))
list_file_ERA5 = glob.glob(os.path.join(path_inputdata, 'ERA5/*.npy'))
list_file_insitu = glob.glob(os.path.join(path_inputdata, 'measured_wind_data/*.npy'))

Data = {}

for station in Stations:
    Data[station] = {}
    ############################################################################
    # Loading data
    ############################################################################
    #
    # ###### Era5Land wind data
    path_ERA5Land = [file for file in list_file_ERA5Land if station in file][0]
    Data_ERA5Land = np.load(path_ERA5Land, allow_pickle=True).item()
    #
    t_era = np.array([i.replace(tzinfo=None) for i in Data_ERA5Land['time']])
    U_era = np.sqrt(Data_ERA5Land['u10']**2 + Data_ERA5Land['v10']**2).squeeze()
    Orientation_era = (np.arctan2(Data_ERA5Land['v10'], Data_ERA5Land['u10'])*180/np.pi).squeeze() % 360
    # ###### in situ wind data
    path_insitu = [file for file in list_file_insitu if station in file][0]
    Data_insitu = np.load(path_insitu, allow_pickle=True).item()
    #
    t_insitu = Data_insitu['time']
    U_insitu = Data_insitu['velocity']
    # putting angles in trigo. ref.
    Orientation_insitu = (270 - Data_insitu['direction']) % 360
    #
    ############################################################################
    # Averaging in situ data over 1hr
    ############################################################################
    dt = timedelta(minutes=60)  # bin size for averaging
    tmin, tmax = t_era[0].replace(minute=0), t_era[-1].replace(minute=50)
    t_insitu_hourly = np.arange(tmin - dt/2, tmax + dt/2, dt).astype(datetime)  # centered on Era5Land time steps
    # #### Using number of seconds from tmin for averaging function
    diff_time_seconds = [i.total_seconds() for i in (t_insitu - tmin)]
    bins_seconds = [i.total_seconds() for i in (t_insitu_hourly - tmin)]
    #
    # #### Averaging into bins
    U_av, bin_edges, _ = binned_statistic(diff_time_seconds, [U_insitu*cosd(Orientation_insitu), U_insitu*sind(Orientation_insitu)],
                                          bins=bins_seconds, statistic=np.nanmean)
    #
    Orientation_av = (np.arctan2(U_av[1, :], U_av[0, :])*180/np.pi) % 360  # orientation time series
    U_av = np.linalg.norm(U_av, axis=0)  # velocity time series
    bin_centered = bin_edges[1:] - (bin_edges[1] - bin_edges[0])/2
    t_insitu_avg = tmin + np.array([timedelta(seconds=i) for i in bin_centered])
    # Note: at this point, the in situ data are mapped on the ERA5 time steps, with a lot of NaNs where there was no in situ data.
    #
    ############################################################################
    # Filtering unusued data (NaNs, 0 velocity)
    ############################################################################
    mask = (~ (np.isnan(U_av) | np.isnan(Orientation_av))) & (U_av > 0)
    #
    # #### Storing data into dictionnary
    Data[station]['U_insitu'] = U_av[mask]
    Data[station]['Orientation_insitu'] = Orientation_av[mask]
    Data[station]['time'] = t_insitu_avg[mask]
    Data[station]['z_insitu'] = Data_insitu['z_mes']
    #
    Data[station]['U_era'] = U_era[mask]
    Data[station]['Orientation_era'] = Orientation_era[mask]
    Data[station]['z_ERA5LAND'] = 10  # [m]
    #
    ############################################################################
    # If available, do the same for the meteorological data from Era5
    ############################################################################
    if station in ['South_Namib_Station', 'Deep_Sea_Station']:
        # BLH
        path_BLH = [file for file in list_file_ERA5 if (station in file) & ('BLH' in file)][0]
        Data_BLH = np.load(path_BLH, allow_pickle=True).item()
        Data[station]['Boundary layer height'] = Data_BLH['blh'].squeeze()[mask]
        # Pressure level data
        path_level = [file for file in list_file_ERA5 if (station in file) & ('levels' in file)][0]
        Data_level = np.load(path_level, allow_pickle=True).item()
        Data[station]['Pressure levels'] = np.array(Data_level['levels'])
        inds_mask = np.arange(t_era.size)[mask]
        for key in Data_level.keys():
            if key not in ['time', 'levels', 'latitude', 'longitude']:
                Data[station][Names[key]] = Data_level[key].squeeze()[..., inds_mask]

path_save = os.path.join(path_outputdata, 'Data_preprocessed.npy')
np.save(path_save, Data)
