#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import time
import numpy as np
import pandas as pd
import hipims_io as hp
from hipims_io.Raster import Raster
file_path = os.path.dirname(os.path.abspath(__file__))
case_path = os.path.dirname(file_path)
# the absolute path of the model executable file
model_name = os.path.dirname(file_path)+'/release/bin/hipims-flood-mgpus'
def run_mg(model_name=model_name, rain_source_file=None, run_time=None):
    """ 
    rain_source_file: 'rain_source_data_1.csv'
    run_time: [0, 10800, 600, 108000]
    """
    start = time.perf_counter()
    input_obj = hp.load_object(case_path+'/obj_in')
    if rain_source_file is not None:
        rain_source_mat = np.loadtxt(rain_source_file, 
                                     delimiter=',')
        rain_source = np.c_[np.arange(0, 3600 * 3, 600),
                            rain_source_mat.transpose() / 3600 / 1000]
        input_obj.set_rainfall(rain_source=rain_source)
        input_obj.write_rainfall_source()
    if run_time is not None:
        input_obj.set_runtime(run_time)
        input_obj.write_runtime_file()
    obj_out = hp.OutputHipims(input_obj)
    output_file_tags = ['h_'+str(t) for t in np.arange(run_time[0], run_time[1]+run_time[2], run_time[2])]
    #output_file_tags.append('h_max_'+str(run_time[1]))
    obj_out.grid_file_tags = output_file_tags
    obj_out.save_object(case_path+'obj_out')
    input_obj.Summary.display()
    time.sleep(5)
    # run model
    os.chdir(input_obj.case_folder)
    os.system(model_name)
    end = time.perf_counter()
    print('Hipims runtime (s):')
    print(end - start)

if __name__ == '__main__':
    run_mg(model_name, rain_source_file=file_path+'/rain_source_data_1.csv', run_time=[0, 1800, 600, 108000])
