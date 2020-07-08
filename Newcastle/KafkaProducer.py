import glob
import os
from kafka import KafkaProducer
from kafka.errors import KafkaError



def send_files():
    print("Connecting to Kafka as producer")
    output_path = "/hipims/Outputs"
    output_files = glob.glob(output_path + "/*.gz")
    print(output_files)
    # Set maxiumum request size to 25000000 bytes (25MB)
    producer = KafkaProducer(bootstrap_servers="10.79.253.132:30002", max_request_size=25000000)
    for file in output_files:
        filename = file[file.rfind("/") + 1:len(file)]
        print("sending " + filename)
        file_handle = open(file, 'rb')
        file_data = file_handle.read()
        print("file size: " + str(len(file_data)) + " bytes")
        # This might be slow since we're reading the entire file to bytes
        response = producer.send(topic="hipims", value=file_data, key=filename)
        try:
            response.get(timeout=10)
        except KafkaError as e:
            print(e)
            pass
        file_handle.close()