#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 29 2020

@author: Xiaodong Ming

"""
import os
import sys
import time
# position storing HiPIMS_IO.py and ArcGridDataProcessing.py
scriptsPath = '../HiPIMS_code/scripts/HiPIMS_IO' 
sys.path.insert(0,scriptsPath)
import numpy as np
import pandas as pd
import hipims_case_class as hp
from myclass import Raster

start = time.perf_counter()
# Create input files
# assume the current dir is the dir to run the model
for N in np.arange(0,8):
    case_folder = os.getcwd()+'/SG/'+str(N)
    data_folder = '../Data'
    dem_file = data_folder+'/DEM2m.gz'
    rain_mask_obj = Raster(data_folder+'/rain_mask_UO_radar.asc')
    rain_source_mat = np.loadtxt(data_folder+'/rain_source_data_1.csv',
                                 delimiter=',')
    rain_source = np.c_[np.arange(0,3600*3, 600),
                        rain_source_mat.transpose()/3600/1000]
    gauges_pos = pd.read_csv(data_folder+'/gauges_pos.csv', delimiter=',')
    gauges_pos = gauges_pos.values[:,1:]
    time_values = [0, 3600*3, 3600*3, 3600*4]
    input_obj = hp.InputHipims(dem_data=dem_file, num_of_sections=1,
                              case_folder=case_folder)
    input_obj.set_device_no(N)
    input_obj.set_runtime(time_values)
    input_obj.set_rainfall(rain_mask=rain_mask_obj.array, rain_source=rain_source)
    input_obj.set_gauges_position(gauges_pos=gauges_pos)
    input_obj.write_input_files()
    input_obj.Summary.write_readme()
    input_obj.save_object(case_folder+'/input_obj.pickle')
    input_obj.Summary.display()
    # run model
    #os.chdir(case_folder)
    #model_name = '../../HiPIMS_code/release/bin/UrbanFloodSimulator'
    #os.system(model_name)
    end = time.perf_counter()
    #print('Model runtime (s):')
    #print(end-start)
