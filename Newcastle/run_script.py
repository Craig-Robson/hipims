import os
import sys
import time
import shutil
from distutils.dir_util import copy_tree
import numpy as np
import pandas as pd
from hipims_io import InputHipims
from hipims_io import OutputHipims
from hipims_io.Raster import Raster
from pypims import flood

simulation_names = ['1','2','3','4','7','8']


def run(simulation_name=''):
    """
    Setup HiPIMS
    """
    data_path = '/hipims/Newcastle/'
    dafni_data_path = os.getenv('DATA_PATH', '/data')
    dafni_output_path = os.path.join(dafni_data_path, 'outputs')


    # create the simulation folder
    case_folder = os.path.join(data_path, 'hipims_case_%s' %simulation_name)

    # get the path to the data

    # should contain the following files

    # ['rain_mask.gz', 'rain_source.csv', 'landcover.gz', 'DEM.gz']

    data_folder = os.path.dirname(os.path.join(data_path))

    # set DEM path

    dem_file = os.path.join(data_folder,'DEM2m.gz')

    # load rainfall data

    rain_mask_obj = Raster(data_folder + '/rain_mask_UO_radar.gz')

    rain_source_mat = np.loadtxt(os.path.join('/hipims/Newcastle/data/%s.csv' %simulation_name), delimiter=',')

    rain_source = np.c_[np.arange(0, 3600 * 12, 600), rain_source_mat.transpose() / 3600 / 1000]

    # load gauge dataexit|()

    gauges_pos = pd.read_csv(data_folder + '/gauges_pos.csv', delimiter=',')

    gauges_pos = gauges_pos.values[:, 1:]

    # time_setup.dat - four values respectively indicate model start time, total time, output interval, and backup interval in seconds
    time_values = [0, 3600 * 12, 600, 3600 * 12]  # [0, 3600 * 1, 600, 3600 * 3]

    # setup input object

    input_obj = InputHipims(dem_data=dem_file, num_of_sections=1, case_folder=case_folder)

    input_obj.set_runtime(time_values)

    input_obj.set_rainfall(rain_mask=rain_mask_obj.array, rain_source=rain_source)

    input_obj.set_gauges_position(gauges_pos=gauges_pos)

    num_gpus = int(1)

    input_obj.set_num_of_sections(num_gpus)

    input_obj_MG = input_obj

    input_obj_MG.write_input_files()

    input_obj_MG.Summary.display()

    # save input object

    input_obj_MG.save_object(case_folder + '/obj_in')

    obj_out = OutputHipims(input_obj_MG)

    output_file_tags = ['h_' + str(t) for t in np.arange(time_values[0], time_values[1] + time_values[2], time_values[2])]

    output_file_tags.append('h_max_' + str(time_values[1]))

    obj_out.grid_file_tags = output_file_tags

    obj_out.save_object(case_folder+'/obj_out')

    # run HIPIMS
    flood.run(case_folder)

    # copy output into DAFNI output directory
    copy_tree('/hipims/Newcastle/hipims_case_dataset_1/output', '/data/outputs')


forecast_id = os.getenv('ForecastID')
run(simulation_name='dataset_%s' %int(forecast_id))
