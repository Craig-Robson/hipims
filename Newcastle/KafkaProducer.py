import glob
import os
from kafka import KafkaProducer

output_path = "/hipims/Outputs"
output_files = glob.glob(output_path + "/*.gz")

def send_files():
    print("Connecting to Kafka as producer")
    # Set maxiumum request size to 25000000 bytes (25MB)
    producer = KafkaProducer(bootstrap_servers="10.79.253.132:30002", max_request_size=25000000)
    for file in output_files:
        filename = file[file.rfind("/") + 1:len(file)]
        print("sending " + filename)
        file_handle = open(file, 'rb')
        # This might be slow since we're reading the entire file to bytes
        producer.send(topic="hipims", value=file_handle.read(), key=filename)
        file_handle.close()