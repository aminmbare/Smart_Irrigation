import requests 
import datetime
import json 
from MyMQTT import * 
import time 
import logging
import os

class ThinkSpeak: 
    def __init__(self,clientID : str,UserID,PlantID, broker : str ,port : int,ThinkSpeakField: dict) -> None:
        self.client = MyMQTT(clientID,broker,port, None)
        self.UserID = UserID
        self.PlantID = PlantID
        self.temperature = None 
        self.humidity = None 
        self.moisture = None 
        self.count = 0
        self._ThinkSpeakField = ThinkSpeakField
        self._headers = {'Content-type': 'application/json', 'Accept': 'raw'}


    def start(self)-> None :
        self.client.start()
    def subscribe(self)->None : 
        temperature_topic = (requests.get(f'http://127.0.0.1:8080/catalog/all_topics?user={self.UserID}&plant={self.PlantID}program=Sensor&type=temperature').json())["topic"]
        moisture_topic = (requests.get(f'http://127.0.0.1:8080/catalog/all_topics?user={self.UserID}&plant={self.PlantID}program=Sensor&type=moisture').json())["topic"]
        humidity_topic = (requests.get(f'http://127.0.0.1:8080/catalog/all_topics?user={self.UserID}&plant={self.PlantID}&program=Sensor&type=humidity').json())["topic"]
        self._topics = [(temperature_topic,0),(moisture_topic,0),(humidity_topic,0)]
        self.client.mySubscribe(self._topics)
    def stop(self)-> None : 
        self.client.stop()
    def notify(self,topic, msg):
        if  topic == "IOT_PROJECT/user1/plant1/temperature/device1": 
            self.temperature = msg["INFO"]["Value"]
        if topic == "IOT_PROJECT/user1/plant1/moisture/device2" : 
            self.moisture = msg["INFO"]["Value"]
        if topic == "IOT_PROJECT/user1/plant1/humidity/device3" :
            self.humidity = msg["INFO"]["Value"]
    def Publish_to_ThingSpeak(self) : 
        data_upload = json.dumps({
            "api_key": self._ThinkSpeakField["api key"],
            "channel_id": self._ThinkSpeakField["channel_id"],
            "created_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "entry_id": self.count,
            "field1":  self.temperature,
            "field2": self.moisture,
            "field3": self.humidity,
        })
        self._count +=1
        headers = {'Content-type': 'application/json', 'Accept': 'raw'}
        requests.post(url=self._ThinkSpeakField["url"], data=data_upload, headers=headers)
        logging.info("Sensor Data has been uploaded to ThingSpeak ")


if __name__ ==  "__main__": 
    logging.basicConfig(level= logging.INFO)
    CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
    Info_path = os.path.join(CURRENT_PATH, "info.json")
    
    with open(Info_path, "r") as f: 
        User_Catalog = json.load(f)
        UserID = User_Catalog["User_ID"]
        PlantID = User_Catalog["Plant_ID"]
        f.close()
    # open ThingSpeak.json and get ThingSpeak User_Catalog
    ThinkSpeakField = requests.get(f"http://127.0.0.1:8080/Catalog/ThingSpeak?user={UserID}&plant={PlantID}").json()
    mqtt_details = requests.get('http://127.0.0.1:8000/Catalog/mqtt_details').json()
    headers = {'Content-type': 'application/json', 'Accept': 'raw'}
    TS = ThinkSpeak("ThinkSpeak_adapter",UserID, PlantID,mqtt_details["broker"],mqtt_details["port"],ThinkSpeakField)
    
    TS.start()
    TS.subscribe()
    
    while True :
        TS.Publish_to_ThingSpeak()
        time.sleep(5)
        
        

    
    
    
    
    
    