import requests 
import datetime
import json 
from MyMQTT import *
import time 
import logging
import os
import ast
from cryptography.fernet import Fernet
class ThinkSpeak: 
    def __init__(self,UserID,PlantID, broker : str ,mqtt_port : int,ThinkSpeakField: dict,catalog_ip : str , catalog_port : str,key: str) -> None:
        self.UserID = UserID
        self.PlantID = PlantID
        self.catalog_ip = catalog_ip
        self.catalog_port = catalog_port
        self.key = key
        self.clientID = "ThinkSpeak_adapter_"+"user"+str(UserID)+"_"+"plant"+str(PlantID)
        self.client = MyMQTT(self.clientID,broker,int(mqtt_port), self)
        self.temperature = None 
        self.humidity = None 
        self.moisture = None 
        self._count_moisture = 0
        self._count_temperature = 0
        self._count_humidity = 0
        self._ThinkSpeakField = ThinkSpeakField
        self._headers = {'Content-type': 'application/json', 'Accept': 'raw'}


    def start(self)-> None :
        self.client.start()
    def subscribe(self,temperature_topic : str , moisture_topic : str , humidity_topic : str)->None : 
        #temperature_topic = (requests.get(f'http://{self.catalog_ip}:{self.catalog_port}/Catalog/topics?user={self.UserID}&plant={self.PlantID}&program=Sensor&type=temperature').json())["topic"]
        #moisture_topic = (requests.get(f'http://{self.catalog_ip}:{self.catalog_port}/Catalog/topics?user={self.UserID}&plant={self.PlantID}&program=Sensor&type=moisture').json())["topic"]
        #humidity_topic = (requests.get(f'http://{self.catalog_ip}:{self.catalog_port}/Catalog/topics?user={self.UserID}&plant={self.PlantID}&program=Sensor&type=humidity').json())["topic"]
        self.temperature_topic = temperature_topic
        self.moisture_topic = moisture_topic
        self.humidity_topic = humidity_topic
        self._topics = [(self.temperature_topic,0),(self.moisture_topic,0),(self.humidity_topic,0)]
        self.client.mySubscribe(self._topics)
    def stop(self)-> None : 
        self.client.stop()
    def notify(self,topic, msg):
        #dict_str = msg.decode("UTF-8")
        #msg = ast.literal_eval(dict_str)
        msg = self.decryptdat(msg)

        logging.info("Received message: " + str(msg) + " on topic: " + str(topic))
        
        if  topic == self.temperature_topic : 
            self.temperature = msg["INFO"]["Value"]
            data_upload = json.dumps({
            "api_key": self._ThinkSpeakField["api key"],
            "channel_id": self._ThinkSpeakField["channel_id"],
            "created_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "entry_id": self._count_temperature,
            "field1":  self.temperature,
            })
            self._count_temperature +=1
            headers = {'Content-type': 'application/json', 'Accept': 'raw'}
            requests.post(url=self._ThinkSpeakField["url"], data=data_upload, headers=headers)
            logging.info("Sensor Data has been uploaded to ThingSpeak ")

        if topic == self.moisture_topic : 
            self.moisture = msg["INFO"]["Value"]
            data_upload = json.dumps({
            "api_key": self._ThinkSpeakField["api key"],
            "channel_id": self._ThinkSpeakField["channel_id"],
            "created_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "entry_id": self._count_moisture,
            "field2": self.moisture,

            })
            self._count_moisture +=1
            headers = {'Content-type': 'application/json', 'Accept': 'raw'}
            requests.post(url=self._ThinkSpeakField["url"], data=data_upload, headers=headers)
            logging.info("Sensor Data has been uploaded to ThingSpeak ")
            logging.info("Moisture value is: " + str(self.moisture))
        
        if topic == self.humidity_topic :
            self.humidity = msg["INFO"]["Value"]
            data_upload = json.dumps({
            "api_key": self._ThinkSpeakField["api key"],
            "channel_id": self._ThinkSpeakField["channel_id"],
            "created_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "entry_id": self._count_humidity,
            "field3": self.humidity,
            })
            self._count_humidity +=1
            headers = {'Content-type': 'application/json', 'Accept': 'raw'}
            requests.post(url=self._ThinkSpeakField["url"], data=data_upload, headers=headers)
            logging.info("Sensor Data has been uploaded to ThingSpeak ")
            logging.info("Humidity value is: " + str(self.humidity))
    
    def decryptdat(self,msg:bytes): 
        f = Fernet(self.key)
        return json.loads(f.decrypt(msg).decode())
  

if __name__ ==  "__main__": 
    logging.basicConfig(level= logging.INFO)
    CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
    Info_path = os.path.join(CURRENT_PATH, "configs.json")
    
    with open(Info_path, "r") as f: 
        configs = json.load(f)
        UserID = configs["User_ID"]
        PlantID = configs["Plant_ID"]
        mqtt_broker = configs["MQTT"]['broker']
        mqtt_port = configs["MQTT"]['port']
        ThinkSpeakField = configs["ThinkSpeak_Field"]
        catalog_ip = configs["Catalog"]["ip_address"]
        catalog_port = configs["Catalog"]["port"]
        key = configs["Encryption_key"].encode('utf-8') 
        temperature_topic = configs["MQTT"]["topics"]["Sensor"]["temperature"]
        humidity_topic = configs["MQTT"]["topics"]["Sensor"]["humidity"]
        moisture_topic = configs["MQTT"]["topics"]["Sensor"]["moisture"]
        f.close()
    # open ThingSpeak.json and get ThingSpeak User_Catalog

    TS = ThinkSpeak(UserID, PlantID,mqtt_broker,mqtt_port,ThinkSpeakField,catalog_ip,catalog_port,key)
    
    TS.start()
    TS.subscribe(temperature_topic, moisture_topic, humidity_topic)
    
    while True :

        time.sleep(5)
        
        

    
    
    
    
    
    