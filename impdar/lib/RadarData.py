#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 dlilien <dlilien90@gmail.com>
#
# Distributed under terms of the GNU GPL3 license.

"""
Define a class that just has the necessary attributes for a stodeep file--this should be subclassed per filetype
"""

import numpy as np
from scipy.io import loadmat, savemat
from scipy.signal import butter, filtfilt
from .horizontal_filters import hfilt, adaptivehfilt


class RadarData():
    # First define all the common attributes
    chan = None
    data = None
    decday = None
    dist = None
    dt = None
    elev = None
    flags = None
    lat = None
    long = None
    pressure = None
    snum = None
    tnum = None
    trace_int = None
    trace_num = None
    travel_time = None
    trig = None
    trig_level = None
    x_coord = None
    y_coord = None

    # Now make some load/save methods that will work with the matlab format
    def __init__(self, fn):
        mat = loadmat(fn)
        for attr in ['chan', 'data', 'decday', 'dist', 'dt', 'elev', 'lat', 'long', 'pressure', 'snum', 'tnum', 'trace_int', 'trace_num', 'travel_time', 'trig', 'trig_level', 'x_coord', 'y_coord']:
            setattr(self, attr, mat[attr])
        self.flags = RadarFlags()
        self.flags.from_matlab(mat['flags'])

    def save(self, fn):
        mat = {}
        for attr in ['chan', 'data', 'decday', 'dist', 'dt', 'elev', 'flags', 'lat', 'long', 'pressure', 'snum', 'tnum', 'trace_int', 'trace_num', 'travel_time', 'trig', 'trig_level', 'x_coord', 'y_coord']:
            mat[attr] = getattr(self, attr)
        savemat(fn, mat)

    def vertical_band_pass(self, low, high, *args, **kwargs):
        # bandpass.m  v3.1 - this function performs a banspass filter in the
        # time-domain of the radar data to remove environmental noise.  The routine
        # currently uses a 5th order Butterworth filter.
        # We have a lot of power to mess with this because scipy. Keeping the butter for now.
        #	
        #Created as stand alone script bandpass.m prior to 1997
        #  Modification history:
        #   1) Input changes made by A. Weitzel 7/10/97
        #   2) Switched to 5th-order Butterworth filter - P. Pearson, 7/2001
        #   3) Coverted for use in StoDeep and added pre-allocation of filtdata
        #       variable - B. Welch 10/2001
        #   4) Filters "stackdata" by default (if it exists),
        #		otherwise filters "data" - Peter Pearson, 2/13/02
        #   5) Now user can filter any standard StoDeep data variable that exists in
        #       memory using a menu displayed for the user - L. Smith, 5/27/03
        #   6) Converted to function and data variable is now passed to the function
        #       rather than selected within the script. - B. Welch, 5/1/06
        #	7) Updated input and outputs to include flags structure. Also added
        #		code to update flags structure - J. Olson 7/10/08
        #	
        # first determine the cut-off corner frequencies - expressed as a
        #	fraction of the Nyquist frequency (half the sample freq).
        # 	Note: all of this is in Hz
        Sample_Freq = 1.0 / self.dt  	# dt=time/sample (seconds)

        #calculate the Nyquist frequency
        Nyquist_Freq = 0.5 * Sample_Freq

        Low_Corner_Freq = low * 1.0e6
        High_Corner_Freq = high * 1.0e6

        corner_freq = np.zeros((2,))
        corner_freq[0] = Low_Corner_Freq / Nyquist_Freq
        corner_freq[1] = High_Corner_Freq / Nyquist_Freq

        b, a = butter(5, corner_freq, 'bandpass')

        # provide feedback to the user
        print('Bandpassing from {:4.1f} to {:4.1f} MHz...'.format(low, high))
        self.data = filtfilt(b, a, self.data, axis=0).astype(self.data.dtype)
        print('Bandpass filter complete.')

        # set flags structure components
        self.flags.bpass[0] = 1
        self.flags.bpass[1] = low
        self.flags.bpass[2] = high

    def hfilt(self, ftype='hfilt', bounds=None):
        if ftype == 'hfilt':
            hfilt(self, bounds[0], bounds[1])
        elif ftype == 'adaptive':
            adaptivehfilt(self)
        else:
            raise ValueError('Unrecognized filter type')


class RadarFlags():

    def __init__(self):
        self.batch = 0
        self.bpass = np.zeros((3,))
        self.hfilt = np.zeros((2,))
        self.rgain = 0
        self.agc = 0
        self.restack = 0
        self.reverse = 0
        self.crop = 0
        self.nmo = 0
        self.interp = 0
        self.mig = 0
        self.elev = 0
        self.attrs = ['batch', 'bpass', 'hfilt', 'rgain', 'agc', 'restack', 'reverse', 'crop', 'nmo', 'interp', 'mig', 'elev']

    def to_matlab(self):
        return {att: getattr(self, att) for att in self.attrs}

    def from_matlab(self, matlab_struct):
        for attr in self.attrs:
            setattr(self, attr, matlab_struct[attr][0][0][0])
