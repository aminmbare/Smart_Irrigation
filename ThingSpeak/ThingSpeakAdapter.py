import requests 
import datetime
import json 
from MyMQTT import * 
import time 
import logging


class ThinkSpeak: 
    def __init__(self,clientID : str, broker : str ,port : int ) -> None:
        self.client = MyMQTT(clientID,broker,port, None)
        
        self.temperature = None 
        self.humidity = None 
        self.moisture = None 
        
    def start(self)-> None :
        self.client.start()
    def subscribe(self)->None : 
        temperature_topic = (requests.get('http://127.0.0.1:8080/catalog/all_topics?program=Sensor&type=temperature').json())["topic"]
        moisture_topic = (requests.get('http://127.0.0.1:8080/catalog/all_topics?program=Sensor&type=moisture').json())["topic"]
        humidity_topic = (requests.get('http://127.0.0.1:8080/catalog/all_topics?program=Sensor&type=humidity').json())["topic"]
        self.__topics = [(temperature_topic,0),(moisture_topic,1),(humidity_topic,2)]
        self.client.mySubscribe(self.__topics)
    def stop(self)-> None : 
        self.client.stop()
    def notify(self,topic, msg):
        if  topic == "IOT_PROJECT/user1/plant1/temperature/device1": 
            self.temperature = msg["INFO"]["Value"]
        if topic == "IOT_PROJECT/user1/plant1/moisture/device2" : 
            self.moisture = msg["INFO"]["Value"]
        if topic == "IOT_PROJECT/user1/plant1/humidity/device3" :
            self.humidity = msg["INFO"]["Value"]


if __name__ ==  "__main__": 
    logging.basicConfig(level= logging.INFO)
    
    ThinkSpeakField = requests.get('http://127.0.0.1:8000/catalog/ThinkSpeak').json()
    mqtt_details = requests.get('http://127.0.0.1:8000/catalog/mqtt_details').json()
    headers = {'Content-type': 'application/json', 'Accept': 'raw'}
    TS = ThinkSpeak("ThinkSpeak_adapter",mqtt_details["broker"],mqtt_details["port"])
    
    TS.start()
    TS.subscribe()
    
    count = 0
    t = 0
    while t < 80:
        data_upload = json.dumps({
            "api_key": ThinkSpeakField["api key"],
            "channel_id": ThinkSpeakField["channel_id"],
            "created_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "entry_id": count,
            "field1":  TS.temperature,
            "field2": TS.moisture,
            "field3": TS.humidity,
           

        })

        requests.post(url=ThinkSpeakField["url"], data=data_upload, headers=headers)
        logging.info("\nINFORMATION SENT TO THINGSPEAK!\n")

        time.sleep(5)
        count += 1
        t += 1

TS.stop()
    
    
    
    
    
    