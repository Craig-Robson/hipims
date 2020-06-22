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
output_folder = '/hipims/Outputs'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
# clean output folder
# files = glob.glob(output_folder+'/*')
# for f in files:
#     os.remove(f)
obj_out = hp.load_object('obj_out')
os.chdir(output_folder)
def combine_save(obj_out=obj_out):
    if hasattr(obj_out, 'Summary'):
        obj_out.Summary.write_readme(output_folder+'/model_infor.txt')
        obj_out.Summary.display()
    # save gauge data
    gauges_pos, times, values = obj_out.read_gauges_file('h')
    print('gauges_pos:')
    print(gauges_pos)
    np.savetxt(output_folder + '/gauges_pos.csv', gauges_pos, fmt='%g', delimiter=',')
    np.savetxt(output_folder + '/gauges_depth.csv', values, fmt='%g', delimiter=',')
    np.savetxt(output_folder + '/time_steps.csv', times, fmt='%g', delimiter=',')
    print('gauge data saved')
    # save grid data
    grid_file_tags = obj_out.grid_file_tags
    for file_tag in grid_file_tags:
        obj_h = obj_out.read_grid_file(file_tag)
        obj_h.to_osgeo_raster(output_folder + "/" + file_tag)
        print(file_tag+'.tif saved')

if __name__ == '__main__':
    combine_save()
