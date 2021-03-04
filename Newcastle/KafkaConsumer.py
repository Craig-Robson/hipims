import gzip
import json
import os
import time

from kafka import KafkaConsumer

import KafkaProducer
import combine_mgpu_results
import run_NCL_2m_MG
import tempfile
import zipfile
import shutil
from datetime import datetime

# consumer = KafkaConsumer(value_deserializer=lambda m: json.loads(m.decode('utf-8')),
#                          bootstrap_servers='19scomps002:9092')

broker_address = os.getenv("BROKER_ADDRESS")
if broker_address == "":
    print(f"Error: Kafka broker address not found. Define broker address at environment variable BROKER_ADDRESS")
    exit(1)


consumer = KafkaConsumer(value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                         bootstrap_servers=broker_address)

consumer.subscribe(['hipims_forecast'])
for message in consumer:
    if message is not None:
        if message.topic == "hipims_forecast":
            print(f"Received {len(message.value) + len(message.key)} bytes at {datetime.now()}")
            print("Unzipping forecasts")
            data = gzip.decompress(message.value)
            tmp = tempfile.mkdtemp()
            tmp_zip = tempfile.NamedTemporaryFile(mode='wb', delete=False)
            tmp_zip.write(data)
            tmp_zip.close()
            with zipfile.ZipFile(tmp_zip, mode='r') as extract:
                extract.extractall(tmp)

            # Unzipped forecasts located in /tmp/{random directory} (Use the tmp variable)

            # TODO Update run_NCL_2m_MG.run_mg to use directory as input
            # with open('rain_source_data_1.csv', mode='wb+') as rain_source:
            #     rain_source.write(data)
            #
            # time.sleep(5)
            # print('data set up...')
            # rain_source_file = os.getcwd()+'/rain_source_data_1.csv'
            # run_NCL_2m_MG.run_mg(rain_source_file=rain_source_file, run_time=[0, 10800, 600, 108000])
            try:
                combine_mgpu_results.combine_save()
            except Exception as e:
                print(e)
                # Ignore any exceptions for now.
                pass
            print("Sending output...")
            KafkaProducer.send_files(broker_address)
            print("Cleaning up input files")
            os.remove(tmp_zip.name)
            shutil.rmtree(tmp)
