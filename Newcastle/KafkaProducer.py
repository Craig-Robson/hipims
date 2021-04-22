import glob

from kafka import KafkaProducer
from kafka.errors import KafkaError


def send_files(broker_address: str, forecast_file: str):
    print(f"Connecting to Kafka at {broker_address}")
    output_path = "/hipims/Outputs"
    output_files = glob.glob(output_path + "/*.gz")
    print(output_files)
    # Set maximum request size to 25000000 bytes (25MB)
    producer = KafkaProducer(bootstrap_servers=broker_address, max_request_size=25000000)
    for file in output_files:
        # Result file name would be 0_
        filename = forecast_file[9:len(forecast_file) - 4] + "_" + file[file.rfind("/") + 1:len(file)]
        print("sending " + filename)
        file_handle = open(file, 'rb')
        file_data = file_handle.read()
        print("file size: " + str(len(file_data)) + " bytes")
        # This might be slow since we're reading the entire file to bytes
        response = producer.send(topic="hipims", value=file_data, key=filename.encode("utf-8"))
        try:
            response.get(timeout=10)
        except KafkaError as e:
            print(e)
            pass
        file_handle.close()
    producer.flush()
    producer.close()
