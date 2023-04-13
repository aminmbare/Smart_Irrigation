from MyMQTT import * 
import datetime 
import requests 
import time 
import random 
import Abstract_Device_Connector
import logging


class device_connector_moisture(Abstract_Device_Connector): 

    def __init__(self ,UserID: str,PlantID: str, DeviceID: str)-> None: 
        super().__init__()
        self.__root = "IOT_PROJECT" 
        self.__UserID = UserID 
        self.__PlantID = PlantID 
        self.__DeviceID = DeviceID 
        self.val_type = "moisture"
        self.ClientID = "Moisture_Connector"+"_"+self.__UserID+"_"+self.__PlantID+"_"+self.__DeviceID
        self.topic = self.__root +"/"+ self.__UserID +"/" + self.__PlantID+"/"+self.val_type\
                     +"/" + self.__DeviceID   
        
        self.message = {"Topic": self.__topic , "ClientID":self.ClientID,
                            "INFO":{"Type":self.val_type , "Value":None , "Time":'',
                            "Unit":"%"}}


        self.client = MyMQTT(self.ClientID, self.broker, self.port, None)


    def start(self): 
        self.client.start()

    def stop(self): 
        self.client.stop()

    def publish(self, value): 
        logging.info("Moisture value is: " + str(value))
        self.message["INFO"]["Time"] = str('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
        self.message["INFO"]["Value"] = value 
        self.client.myPublish(self.topic, self.message)

if __name__ == "__main__": 

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    UserID = "user1"       
    PlantID = "plant1"
    DeviceID =  "device2"
    moisture = device_connector_moisture( UserID, PlantID, DeviceID)
    moisture.start()
    logging.info(" Moisture Connector is active\n")
    """  Finish the LAST part """
    while True : 
        i = 80
        while i<= 95 : 
            temp = i
            moisture.publish(temp)
            i = random.choice([0,1,0.5])
            time.sleep(4)
        while i >= 50: 
            temp = i 
            moisture.publish(temp)
            i -= random.choice([0,1,0.5])
            time.sleep(4)