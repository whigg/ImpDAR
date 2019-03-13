#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 dlilien <dlilien@berens>
#
# Distributed under terms of the GNU GPL3 license.

"""
Loading of SEGY files.
"""
import segyio
import numpy as np
from .RadarData import RadarData, RadarFlags


class SEGY(RadarData):

    def __init__(self, fn):
        self.f = segyio.open(fn, ignore_geometry=True)
        self.data = np.array([trace for trace in self.f.trace[:]]).transpose()
        self.snum = self.f.bin[segyio.BinField.Samples]
        self.tnum = self.data.shape[1]
        self.dt = self.f.bin[segyio.BinField.Interval] / 1.
        self.trace_num = np.arange(self.data.shape[1]) + 1
        self.trig_level = np.zeros((self.tnum, ))
        self.pressure = np.zeros((self.tnum, ))
        self.flags = RadarFlags()
        self.travel_time = np.atleast_2d(np.arange(0, self.dt * self.snum, self.dt)).transpose() + self.dt

 
def load_segy(fn, *args, **kwargs):
    return SEGY(fn)
