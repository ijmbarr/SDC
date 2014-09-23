"""
Tools to help with data analysis for the Summer Data Science Challenge
"""

import numpy as np
import pandas as pd
import matplotlib.plt as plt

def longLatDist(p1, p2): 
    '''Takes two pairs of (long,lat) and returns distance between them (using small angle approx)'''
    R = 6371 #Earth Radius in kilometers
    dx = R*np.cos(np.radians(p1[0]))*np.radians(p1[0] - p2[0])
    dy = R*np.radians(p1[1] - p2[1])
    return np.sqrt( dx**2 + dy**2 )