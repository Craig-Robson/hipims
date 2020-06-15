import os
import sys
import time
import numpy as np
import pandas as pd
from hipims_io import InputHipims
#from hipims_io import OutputHipims
from hipims_io.Raster import Raster
file_path = os.path.dirname(os.path.abspath(__file__))
data_folder = file_path # data folder is the same with this script
# case_folder is the path to store input and output data of Hipims
case_folder = file_path+'/Model' 
# the absolute path of the model executable file
model_name = os.path.dirname(file_path)+'/release/bin/hipims-flood-mgpus'
def run_mg(case_folder, model_name, num_gpus=8):
    start = time.perf_counter()
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
    input_obj.write_input_files()
    input_obj.Summary.display()
    # run model
    os.chdir(case_folder)
    os.system(model_name)
    end = time.perf_counter()
    print('Model runtime (s):')
    print(end - start)


if __name__ == '__main__':
    run_mg(case_folder, model_name)
