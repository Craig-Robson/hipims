#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 29 2020

@author: Xiaodong Ming

"""
import sys
root_path = '/home/nxm8/Newcastle/'
sys.path.insert(0,root_path+'HiPIMS_code/scripts/HiPIMS_IO')
import time
import os
import numpy as np
import hipims_case_class as hp
import hipims_post_process as hpp
# from multiprocessing import Pool


start = time.perf_counter()
# Create input files
def run_save_model(gpu_ID):
    case_ids = [49,50]#np.arange(1,26)+gpu_ID*25
    root_path = '/home/nxm8/Newcastle/'
    for N in case_ids:
        print('case_id: '+str(N))
        print('gpu_id: '+str(gpu_ID))
        case_folder = root_path+'Model/SG/'+str(gpu_ID)
        input_obj = hp.load_object(case_folder+'/input_obj.pickle')
        rain_file_name = root_path+'Data/raindata0214/data_'+str(N)+'.csv'
        rain_source_mat = np.loadtxt(rain_file_name, delimiter=',')
        rain_source = np.c_[np.arange(0,3600*3, 600),
                            rain_source_mat.transpose()/3600/1000]
        input_obj.set_rainfall(rain_source=rain_source)
        input_obj.write_rainfall_source()
        input_obj.Summary.write_readme(case_folder+'/readme_'+str(N)+'.txt')
        # input_obj.save_object(case_folder+'/input_obj'+
        #                       str(case_ids)+'-'+str(gpu_ID))
        input_obj.Summary.display()
        # run model
        os.chdir(case_folder)
        model_name = root_path+'HiPIMS_code/release/bin/UrbanFloodSimulator'
        os.system(model_name)
        # read and save results
        obj_output = hpp.OutputHipims(input_obj)
        obj_output.add_grid_results(['h_max_10800'])
        # obj_output.add_all_gauge()
        h_value = np.loadtxt(case_folder+'/output/h_gauges.dat', 
                             dtype='float64', ndmin=2)
        obj_output.h_value = h_value
        obj_output.case_id = N
        output_path = root_path+'Model/SG/output_all'
        obj_output.save_object(output_path+'/output_'+str(N))
        print(output_path+'/output_'+str(N))
        print('Model runtime (s):')
        end = time.perf_counter()
        print(end-start)
    
gpu_ID = int(input('GPU:\n'))
run_save_model(gpu_ID)
# p = Pool(8)
# for i in np.arange(8):
#     p.apply_async(run_save_model, args=(i,))
# print('Waiting for all subprocesses done...')
# p.close()
# p.join()
# print('All subprocesses done.')
