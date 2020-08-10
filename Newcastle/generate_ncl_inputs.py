import os
import sys
import time
import numpy as np
import pandas as pd
from hipims_io import InputHipims
from hipims_io import OutputHipims
from hipims_io.Raster import Raster
file_path = os.path.dirname(os.path.abspath(__file__))
data_folder = file_path # data folder is the same with this script
# case_folder is the path to store input and output data of Hipims
case_folder = os.path.dirname(file_path)+'/Model_IO' 
dem_file = data_folder + '/DEM2m.gz'
# load rainfall data
rain_mask_obj = Raster(data_folder + '/rain_mask_UO_radar.gz')
rain_source_mat = np.loadtxt(data_folder + '/rain_source_data_1.csv',
                                 delimiter=',')
rain_source = np.c_[np.arange(0, 3600 * 3, 600),
                        rain_source_mat.transpose() / 3600 / 1000]
# load gauge data
gauges_pos = pd.read_csv(data_folder + '/gauges_pos.csv', delimiter=',')
gauges_pos = gauges_pos.values[:, 1:]
time_values = [0, 3600 * 1, 600, 3600 * 3]
# setup input object
input_obj = InputHipims(dem_data=dem_file, num_of_sections=1,
                               case_folder=case_folder)
input_obj.set_runtime(time_values)
input_obj.set_rainfall(rain_mask=rain_mask_obj.array, rain_source=rain_source)
input_obj.set_gauges_position(gauges_pos=gauges_pos)
# write input files
def setup_model():
    args = sys.argv
    if len(args)==2:
        num_gpus = int(args[1])
        input_obj_MG = input_obj.set_num_of_sections(num_gpus)
        input_obj_MG.write_input_files()
        input_obj_MG.Summary.display()
        # save input object
        input_obj_MG.save_object('obj_in')
        obj_out = OutputHipims(input_obj_MG)
        output_file_tags = ['h_'+str(t) for t in np.arange(time_values[0], time_values[1]+time_values[2], time_values[2])]
        output_file_tags.append('h_max_'+str(time_values[1]))
        obj_out.grid_file_tags = output_file_tags
        obj_out.save_object('obj_out')
    else:
        raise IOError('Only one int parameter is needed.')
if __name__=='__main__':
    setup_model()
