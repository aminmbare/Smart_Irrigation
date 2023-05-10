from MyMQTT import * 
import datetime 
import requests 
import time 
import random 
from  Abstract_Device_Connector import device_connector
import logging
import os

class device_connector_moisture(device_connector): 

    def __init__(self ,UserID: str,PlantID: str,TS: dict)-> None: 
        super(device_connector_moisture,self).__init__()
        self._root = "IOT_PROJECT" 
        self._UserID = "user"+UserID 
        self._PlantID = "plant"+PlantID 
        self._DeviceID = "device2"
        self._val_type = "moisture"
        self._ClientID = "Moisture_Connector"+"_"+self._UserID+"_"+self._PlantID+"_"+self._DeviceID
        self._topic = (requests.get(f'http://127.0.0.1:8080/Catalog/topics?user={self._UserID[-1]}&plant={self._PlantID[-1]}&program=Sensor&type=moisture').json())["topic"] 
        
        self._message = {"Topic": self._topic , "ClientID":self._ClientID,
                            "INFO":{"Type":self._val_type , "Value":None , "Time":'',
                            "Unit":"%"}}


        self.client = MyMQTT(self._ClientID, self.broker, self.port, None)
        
        self._TS = TS
        self._count = 0
        


    def start(self): 
        self.client.start()

    def stop(self): 
        self.client.stop()

    def publish(self, value): 
        logging.info("Moisture value is: " + str(value))
        self._message["INFO"]["Time"] = str('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
        self._message["INFO"]["Value"] = value 
        logging.info("Topic is: " + self._topic)
        self.client.myPublish(self._topic, self._message)
        # Upload to ThingSpeak
        data_upload = json.dumps({
            "api_key": self._TS["api key"],
            "channel_id": self._TS["channel_id"],
            "created_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "entry_id": self._count,
            "field3":  value,      
        })
        self._count +=1
        headers = {'Content-type': 'application/json', 'Accept': 'raw'}
        requests.post(url=self._TS["url"], data=data_upload, headers=headers)


if __name__ == "__main__": 

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
    Info_path = os.path.join(CURRENT_PATH, "info.json")
    with open(Info_path, "r") as f: 
        info = json.load(f)
        UserID = info["User_ID"]
        PlantID = info["Plant_ID"]

        f.close()
    ThinkSpeak = requests.get(f"http://127.0.0.1:8080/Catalog/ThingSpeak?user={UserID}&plant={PlantID}").json()
    moisture = device_connector_moisture( UserID, PlantID,ThinkSpeak)
    moisture.start()
    logging.info(f" Moisture Connector for {UserID}, {PlantID} is started  ")
    """  Finish the LAST part """
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