import argparse
import gzip
import json
import os
import time

from kafka import KafkaConsumer

import KafkaProducer
import combine_mgpu_results
import run_NCL_2m_MG

# consumer = KafkaConsumer(value_deserializer=lambda m: json.loads(m.decode('utf-8')),
#                          bootstrap_servers='19scomps002:9092')

broker_address = os.getenv("BROKER_ADDRESS")
if broker_address == "":
    parser = argparse.ArgumentParser(description="Hipims for flood prepared")
    parser.add_argument("broker_address", type=str, help="Kafka broker address")
    args = parser.parse_args()
    broker_address = args.broker_address

consumer = KafkaConsumer(value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                         bootstrap_servers=broker_address)

consumer.subscribe(['hipims_res'])
for message in consumer:
    if message is not None:
        if message.topic == "hipims_forecast":
            print(message)
            data = gzip.decompress(message.value)

            with open('rain_source_data_1.csv', encoding='utf-8', mode='w+') as rain_source:
                rain_source.write(data)

            time.sleep(5)
            print('data set up...')
            rain_source_file = os.getcwd()+'/rain_source_data_1.csv'
            run_NCL_2m_MG.run_mg(rain_source_file=rain_source_file, run_time=[0, 10800, 600, 108000])
            try:
                combine_mgpu_results.combine_save()
            except Exception as e:
                print(e)
                # Ignore any exceptions for now.
                pass
            KafkaProducer.send_files()
