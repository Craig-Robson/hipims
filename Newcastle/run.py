import gzip
import json
import os
import time

import combine_mgpu_results
import run_NCL_2m_MG
import tempfile
import zipfile
import shutil
from datetime import datetime

print("Running")
print("Unzipping forecasts")

data = '/hipims/Newcastle/rain_source_data_1.csv'
tmp = tempfile.mkdtemp()
shutil.copyfile(data,tmp+'/rain_source_data_1.csv')

hours_to_run = 12

# Unzipped forecasts located in /tmp/{random directory} (Use the tmp variable)
print(f"Starting simulation at {datetime.now()}")
for forecast_file in os.listdir(tmp):
    print(f"Running simulator for {forecast_file}...")
    run_NCL_2m_MG.run_mg(rain_source_file=os.path.join(tmp, forecast_file), run_time=[0, 3600 * 12, 600, 3600 * 12 * 10])
    print(f"Combining results...")
    try:
        combine_mgpu_results.combine_save()
    except Exception as e:
        print(e)
        # Ignore any exceptions for now.
        pass
    print(f"Sending output to Kafka")

    print(f"Preparing next simulation...")
    output_path = "/hipims/Outputs"
    for hipims_output in os.listdir(output_path):
        print('copy files to output dir')

# with open('rain_source_data_1.csv', mode='wb+') as rain_source:
#     rain_source.write(data)
#
# time.sleep(5)
# print('data set up...')
# rain_source_file = os.getcwd()+'/rain_source_data_1.csv'
# run_NCL_2m_MG.run_mg(rain_source_file=rain_source_file, run_time=[0, 10800, 600, 108000])
print(f"Simulation ended at {datetime.now()}")
print("Cleaning up input files")
shutil.rmtree(tmp)
