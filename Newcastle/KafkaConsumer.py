import gzip
import json
import os
import time

from kafka import KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic

import KafkaProducer
import combine_mgpu_results
import run_NCL_2m_MG
import tempfile
import zipfile
import shutil
from datetime import datetime

broker_address = os.getenv("BROKER_ADDRESS")
if broker_address == "":
    print(f"Error: Kafka broker address not found. Define broker address at environment variable BROKER_ADDRESS")
    exit(1)

topics = ["hipims_forecast"]
producer_topics = ["hipims"]
# Consumer can pull up to 25 MB
consumer = KafkaConsumer(bootstrap_servers=broker_address, max_partition_fetch_bytes=25000000)
# Check for current made topics
current_topics = consumer.topics()
topics_to_create = set(topics).union(set(producer_topics)) - current_topics
# Create new topics if it does not exist
# By default Kafka will automatically create the topics if the consumer subscribes to a topic that does not exist
# However, Kafka replies the clients that the topic doesn't exist before creating the topics,
# causing the consumers to fail
# In Java, the consumers will throw an exception
# But in Python, the consumers will silently fail (if logging is not configured)
admin_client = KafkaAdminClient(bootstrap_servers=broker_address)
new_topics = []
for name in topics_to_create:
    print(f"Topic {name} does not exist. Creating one")
    new_topics.append(NewTopic(name=name, num_partitions=1, replication_factor=1))
admin_client.create_topics(new_topics=new_topics, validate_only=False)
admin_client.close()

consumer.subscribe(topics)
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
