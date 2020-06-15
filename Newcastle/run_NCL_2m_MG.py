import os
import sys
import time
import numpy as np
import pandas as pd
import hipims_io as hp
from hipims_io.Raster import Raster
file_path = os.path.dirname(os.path.abspath(__file__))
# the absolute path of the model executable file
model_name = os.path.dirname(file_path)+'/release/bin/hipims-flood-mgpus'
def run_mg(model_name):
    start = time.perf_counter()
    input_obj = hp.load_object('obj_in')
    input_obj.Summary.display()
    # run model
    os.chdir(input_obj.case_folder)
    os.system(model_name)
    end = time.perf_counter()
    print('Model runtime (s):')
    print(end - start)


if __name__ == '__main__':
    run_mg(model_name)
