#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2019 David Lilien <dlilien90@gmail.com>
#
# Distributed under terms of the GNU GPL3 license.

"""
Loading of SEGY files.
"""
import numpy as np
from ..RadarData import RadarData
from ..RadarFlags import RadarFlags

try:
    import segyio
    SEGY = True
except ImportError:
    SEGY = False

def load_segy(fn_sgy, *args, **kwargs):
    """Load segy data. This is very generic for now,
    need to do work if there are particular types of segy files that need to be read"""
    if not SEGY:
        raise ImportError('Need segyio to load SGY files')
    segy_data = RadarData(None)
    segy_data.f = segyio.open(fn_sgy, ignore_geometry=True)
    where_good = np.where(segy_data.f.attributes(
        segyio.TraceField.SourceX)[:] == segy_data.f.attributes(segyio.TraceField.SourceX)[0])[0]
    segy_data.data = segyio.tools.collect(
        segy_data.f.trace[where_good[0]:where_good[-1] + 1]).transpose()
    segy_data.snum = segy_data.f.bin[segyio.BinField.Samples]
    segy_data.tnum = segy_data.data.shape[1]
    segy_data.dt = segy_data.f.bin[segyio.BinField.Interval]
    segy_data.trace_num = np.arange(segy_data.data.shape[1]) + 1
    segy_data.trig_level = np.zeros((segy_data.tnum, ))
    segy_data.pressure = np.zeros((segy_data.tnum, ))
    segy_data.flags = RadarFlags()
    # segy_data.travel_time = np.atleast_2d(np.arange(0,
    # segy_data.dt * segy_data.snum, segy_data.dt)).transpose()
    # + segy_data.dt
    return segy_data
