import sys
import os

from Abstract_Device_Connector import device_connector
from MyMQTT import * 
import datetime  
import logging
import time 
import random 
import requests



class device_connector_humidity(device_connector): 

    def __init__(self , UserID : int, PlantID: int ,TS : dict)-> None: 
        super(device_connector_humidity,self).__init__()
        self._root = "IOT_PROJECT" 
        self._UserID = "user"+UserID 
        self._PlantID = "plant"+PlantID 
        self._DeviceID = "device3"
        self._val_type = "humidity"
        self._ClientID = "Humidity_Connector_"+self._UserID+"_"+self._PlantID+"_"+self._DeviceID
        self._topic = (requests.get(f'http://127.0.0.1:8080/Catalog/topics?user={self._UserID[-1]}&plant={self._PlantID[-1]}&program=Sensor&type=humidity').json())["topic"]
        
        self._message = {"Topic": self._topic , "ClientID":self._ClientID,
                            "INFO":{"Type":self._val_type , "Value":None , "Time":'',
                            "Unit":'%'}}
        
        self._TS = TS
        self._count = 0
        self.client = MyMQTT(self._ClientID, self.broker, self.port, None)
        

    def start(self)-> None: 
        self.client.start()

    def stop(self)-> None: 
        self.client.stop()

    def publish(self, value) -> None: 
        logging.info("Moisture value is: " + str(value))
        self._message["INFO"]["Time"] = str('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
        self._message["INFO"]["Value"] = value 
        self.client.myPublish(self._topic, self._message)
        ## Upload to ThingSpeak
        data_upload = json.dumps({
            "api_key": self._TS["api key"],
            "channel_id": self._TS["channel_id"],
            "created_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "entry_id": self._count,
            "field2":  value,      
        })
        self._count +=1
        headers = {'Content-type': 'application/json', 'Accept': 'raw'}
        requests.post(url=self._TS["url"], data=data_upload, headers=headers)

if __name__ == "__main__": 
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    # open info.json and get User ID and Plant ID
    CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
    Info_path = os.path.join(CURRENT_PATH, "info.json")
    with open(Info_path, "r") as f: 
        info = json.load(f)
        UserID = info["User_ID"]
        PlantID = info["Plant_ID"]
        f.close()
    logging.info(f" User ID is {UserID} , Plant ID is {PlantID}  ")
    ThinkSpeak = requests.get(f"http://127.0.0.1:8080/Catalog/ThingSpeak?user={UserID}&plant={PlantID}").json()
    
    humidity = device_connector_humidity(UserID, PlantID,ThinkSpeak)
    humidity.start()
    logging.info(f" Humidity Connector for {UserID}, {PlantID}  is activated  ")
    
    while True : 
        i = 80
        while i<= 95 : 
            temp = i
            humidity.publish(temp)
            i += random.choice([0,1,0.5])
            time.sleep(4)
        while i >= 50: 
            temp = i 
            humidity.publish(temp)
            i -= random.choice([0,1,0.5])
            time.sleep(4)
    
