#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on TUE Jun 16 2020
@author: Xiaodong Ming
"""
import os
import glob
import time
import numpy as np
import hipims_io as hp
file_path = os.path.dirname(os.path.abspath(__file__))
# output_folder is the path to store output data of Hipims
output_folder = os.path.dirname(file_path)+'/Outputs'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
# clean output folder
files = glob.glob(output_folder+'/*')
for f in files:
    os.remove(f)
obj_out = hp.load_object('obj_out')
os.chdir(output_folder)
def combine_save(obj_out=obj_out):
    if hasattr(obj_out, 'Summary'):
        obj_out.Summary.write_readme(output_folder+'/model_infor.txt')
    # save gauge data
    gauges_pos, times, values = obj_out.read_gauges_file('h')
    np.savetxt('gauges_pos.csv', gauges_pos, fmt='%g', delimiter=',')
    np.savetxt('gauges_depth.csv', values, fmt='%g', delimiter=',')
    np.savetxt('time_steps.csv', times, fmt='%g', delimiter=',')
    print('gauge data saved')
    # save grid data
    grid_file_tags = obj_out.grid_file_tags
    for file_tag in grid_file_tags:
        obj_h = obj_out.read_grid_file(file_tag)
        obj_h.to_osgeo_raster(file_tag)
        print(file_tag+'.tif saved')

if __name__ == '__main__':
    combine_save()
