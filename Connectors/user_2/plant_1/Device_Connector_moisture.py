from MyMQTT import * 
import datetime 
import requests 
import time 
import random 
from  Abstract_Device_Connector import device_connector
import logging
import os

class device_connector_moisture(device_connector): 

    def __init__(self ,UserID: str,PlantID: str)-> None: 
        super(device_connector_moisture,self).__init__()
        self._root = "IOT_PROJECT" 
        self._UserID = "user"+UserID 
        self._PlantID = "plant"+PlantID 
        self._DeviceID = "device2"
        self._val_type = "moisture"
        self._ClientID = "Moisture_Connector"+"_"+self._UserID+"_"+self._PlantID+"_"+self._DeviceID
        #self._topic = (requests.get(f'http://{self.catalog_address}:{self.catalog_port}/Catalog/topics?user={self._UserID[-1]}&plant={self._PlantID[-1]}&program=Sensor&type=moisture').json())["topic"] 
        
        self._message = {"Topic": self.moisture_topic , "ClientID":self._ClientID,
                            "INFO":{"Type":self._val_type , "Value":None , "Time":'',
                            "Unit":"%"}}

        self.client = MyMQTT(self._ClientID, self.broker, self.mqtt_port, None)
        

        


    def start(self): 
        self.client.start()

    def stop(self): 
        self.client.stop()

    def publish(self, value): 
        logging.info("Moisture value is: " + str(value))
        self._message["INFO"]["Time"] = str('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
        self._message["INFO"]["Value"] = value 
        logging.info("Topic is: " + self.moisture_topic)
        encrypted_message=self.encryptdat(self._message)
        self.client.myPublish(self.moisture_topic, encrypted_message)
        

if __name__ == "__main__": 

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
    configs_path = os.path.join(CURRENT_PATH, "configs.json")
    with open(configs_path, "r") as f: 
        configs = json.load(f)
        UserID = configs["User_ID"]
        PlantID = configs["Plant_ID"]

        f.close()
    moisture = device_connector_moisture(UserID, PlantID)
    moisture.start()
    logging.info(f" Moisture Connector for {UserID}, {PlantID} is started  ")
    while True : 
        i = 400
        while i<= 300 : 
            temp = i
            moisture.publish(temp)
            i += random.choice([0,1,2])
            time.sleep(4)
        while i >= 20: 
            temp = i 
            moisture.publish(temp)
            i -= random.choice([0,1,2])
            time.sleep(4)