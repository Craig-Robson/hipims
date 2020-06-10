import os
import sys
import time
import numpy as np
import pandas as pd
from hipims_io import InputHipims
#from hipims_io import OutputHipims
from hipims_io.Raster import Raster

def run_mg():
    start = time.perf_counter()
    # Create input files
    # assume the current dir is the dir to run the model
    case_folder = os.getcwd() + '/MG'
    num_gpus = 8
    data_folder = '../Data'
    dem_file = data_folder + '/DEM2m.gz'
    rain_mask_obj = Raster(data_folder + '/rain_mask_UO_radar.asc')
    rain_source_mat = np.loadtxt(data_folder + '/rain_source_data_1.csv',
                                 delimiter=',')
    rain_source = np.c_[np.arange(0, 3600 * 3, 600),
                        rain_source_mat.transpose() / 3600 / 1000]
    gauges_pos = pd.read_csv(data_folder + '/gauges_pos.csv', delimiter=',')
    gauges_pos = gauges_pos.values[:, 1:]
    time_values = [0, 3600 * 3, 600, 3600 * 3]
    input_obj = InputHipims(dem_data=dem_file, num_of_sections=num_gpus,
                               case_folder=case_folder)
    input_obj.set_runtime(time_values)
    #input_obj.set_device_no([0,1,2,3]) #Tesla K80
    input_obj.set_rainfall(rain_mask=rain_mask_obj.array, rain_source=rain_source)
    input_obj.set_gauges_position(gauges_pos=gauges_pos)
    # case_obj.Summary.add_items('Reference datetime', '2019-06-10 03:00')
    input_obj.write_input_files()
    input_obj.Summary.write_readme()
    #input_obj.save_object(case_folder + '/input_obj_MG.pickle')
    input_obj.Summary.display()
    # run model
    os.chdir(case_folder)
    model_name = '../../hipims/release/bin/hipims-flood-mgpus'
    os.system(model_name)
    end = time.perf_counter()
    print('Model runtime (s):')
    print(end - start)


if __name__ == '__main__':
    run_mg()
