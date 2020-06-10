import json
import time
import run_NCL_2m_MG

import pandas as pandas
from kafka import KafkaConsumer

# consumer = KafkaConsumer(value_deserializer=lambda m: json.loads(m.decode('utf-8')),
#                          bootstrap_servers='19scomps002:9092')

consumer = KafkaConsumer(value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                         bootstrap_servers='10.79.253.132:30002')

consumer.subscribe(['forecast'])
for message in consumer:
    if message is not None:
        print(message)
        data = message.value
        # print(data)
        with open('test.json', 'w') as json_file:
            json.dump(data, json_file)

        df1 = pandas.read_json('test.json')
        # print(df1)
        df1.to_csv('/home/nxm8/Newcastle/Data/rain_source_data_1.csv', encoding='utf-8', index=False, index_label=False, header=None)
        time.sleep(5)
        print('data set up...')
        run_NCL_2m_MG.run_mg()
