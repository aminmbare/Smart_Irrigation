import os
from Abstract_Device_Connector import device_connector
from MyMQTT import * 
import datetime  
import logging
import time 
import random 


class device_connector_humidity(device_connector): 

    def __init__(self , UserID : int, PlantID: int )-> None: 
        super(device_connector_humidity,self).__init__()
        self._root = "IOT_PROJECT" 
        self._UserID = "user"+UserID 
        self._PlantID = "plant"+PlantID 
        self._DeviceID = "device3"
        self._val_type = "humidity"
        self._ClientID = "Humidity_Connector_"+self._UserID+"_"+self._PlantID+"_"+self._DeviceID
        #self._topic = (requests.get(f'http://{self.catalog_address}:{self.catalog_port}/Catalog/topics?user={self._UserID[-1]}&plant={self._PlantID[-1]}&program=Sensor&type=humidity').json())["topic"]
        
        self._message = {"Topic": self.humidity_topic , "ClientID":self._ClientID,
                            "INFO":{"Type":self._val_type , "Value":None , "Time":'',
                            "Unit":'%'}}
        
        self.client = MyMQTT(self._ClientID, self.broker, self.mqtt_port, None)
        

    def start(self)-> None: 
        self.client.start()

    def stop(self)-> None: 
        self.client.stop()

    def publish(self, value) -> None: 
        logging.info("Humidity value is: " + str(value))
        self._message["INFO"]["Time"] = str('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
        self._message["INFO"]["Value"] = value 
        encrypted_message=self.encryptdat(self._message)
        self.client.myPublish(self.humidity_topic, encrypted_message)
        
if __name__ == "__main__": 
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    # open info.json and get User ID and Plant ID
    CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
    configs_path = os.path.join(CURRENT_PATH, "configs.json")
    with open(configs_path, "r") as f: 
        configs = json.load(f)
        UserID = configs["User_ID"]
        PlantID = configs["Plant_ID"]

        f.close()
    logging.info(f" User ID is {UserID} , Plant ID is {PlantID}  ")

    
    humidity = device_connector_humidity(UserID, PlantID)
    humidity.start()
    logging.info(f" Humidity Connector for user {UserID}, plant {PlantID}  is activated  ")
    
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
    
