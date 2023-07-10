from MyMQTT import * 
import datetime 
import requests 
import time 
from  Abstract_Device_Connector import device_connector
import logging
import os


class device_connector_temp(device_connector): 

    def __init__(self , UserID:int, PlantID: int )-> None: 
        super(device_connector_temp,self).__init__()
        self._root = "IOT_PROJECT"
        self._UserID = "user"+UserID 
        self._PlantID = "plant"+PlantID 
        self._DeviceID = "device"
        self._val_type = "temperature"
        self._ClientID = "Temperature_Connector"+"_"+self._UserID+"_"+self._PlantID+"_"+self._DeviceID
        #self._topic = (requests.get(f'http://{self.catalog_address}:{self.catalog_port}/Catalog/topics?user={self._UserID[-1]}&plant={self._PlantID[-1]}&program=Sensor&type=temperature').json())["topic"]
        self._message = {"Topic": self.temperature_topic , "ClientID":self._ClientID,
                            "INFO":{"Type":self._val_type , "Value":None , "Time":'',
                            "Unit":'Celsius'}}


        self.client = MyMQTT(self._ClientID, self.broker, self.mqtt_port, None)


        self._count = 0
    def start(self): 
        self.client.start()

    def stop(self): 
        self.client.stop()
 

    def publish(self, value)-> None: 
        logging.info("Temperature value is: " + str(value))
        self._message["INFO"]["Time"] = str('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
        self._message["INFO"]["Value"] = value 
        encrypted_message=self.encryptdat(self._message)
        self.client.myPublish(self.temperature_topic, encrypted_message)

    
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
    temperature = device_connector_temp(UserID, PlantID)
    temperature.start()
    logging.info(f" Temperature Connector for user : {UserID}, plant : {PlantID}  is activated  ")
    while True : 
        i = 20 
        while i<= 28 : 
            temp = i 
            temperature.publish(temp)
            i+=1 
            time.sleep(4)
        while i >= 14: 
            temp = i 
            temperature.publish(temp)
            i -= 1 
            time.sleep(4)
            

   