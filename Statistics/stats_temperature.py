import datetime 

import requests 
import logging 
import json
import MyMQTT
import time
import Statistics
class Statistics_humidity(Statistics):
    def __init__(self) -> None:
        super().__init__()
        self.__CliendID = "MoistureStatistics"
        self.client = MyMQTT(self.__CliendID,self.__broker,self.__port,None)
        
    def start(self)-> None: 
        self.client.start()
    def stop(self)-> None : 
        self.client.stop()
    def subsscribe(self,topic : str)-> None : 
        self.client.MySubscribe(topic)
    def notify(self,topic,msg): 
        message = json.loads(msg)
        value = message["INFO"]["Value"]
        unit = message["INFO"]["Unit"]
        timestamp = message["INFO"]["Time"]
        client = message["ClientID"]
        subs = topic.split("/")
        userID , PlantID , valuetype , DeviceID =  subs[1], subs[2] , subs[3], subs[4]
        requests.post('http://127.0.0.1:8080/statistics/Humidity',json.dumps({"value": userID + "-" + PlantID + "-"  + DeviceID + "-" + str(value)}))  
        logging.info(f'Sensor of {valuetype} is measuring {self.value} {unit} at time {timestamp} coming on topic {topic} from {client}')    

@staticmethod
def record_temp(userID, plantID, temp_data): 
    values =  [[],[]]
    time_now = datetime.datetime.now()
    # 24 hours prior
    init_time = time_now - datetime.deltatime(days = 1)

    for i in range(len(temp_data)): 
        timestamp = datetime.datetime.strptime(temp_data[i]['time'], '%d/%m/%Y %H:%M:%S')

        if timestamp > init_time and timestamp < time_now : 
            parsed = temp_data[i]["value"].split("-")
            if parsed[0] == userID and parsed[1] == plantID:
                values[0].append(str(parsed[-1]+"°C"))
                values[1].append(str(timestamp))
    return values


if __name__ == "__main__":
        
    topics = (requests.get('http://127.0.0.1:8080/catalog/all_topics?program=Statistics&type=temperature').json())["topic"]

    Statistics = Statistics_humidity()
    Statistics.start()
    for topic in topics: 
        Statistics.subscribe(topic)
    while True :
        time.sleep(2)