from MyMQTT import * 
import datetime 
import requests 
import time 
import random 
import Abstract_Device_Connector
import logging


class device_connector_temp(Abstract_Device_Connector): 

    def __init__(self , UserID:int, PlantID: int , DeviceID: int )-> None: 
        super().__init__()
        self.__root = "IOT_PROJECT"
        self.__UserID = UserID 
        self.__PlantID = PlantID 
        self.__DeviceID = DeviceID 
        self.ClientID = "Temperature_Connector"+"_"+self.__UserID+"_"+self.__PlantID+"_"+self.__DeviceID
        self.topic = self.__root +"/"+ self.__UserID +"/" + self.__PlantID+"/"+self.val_type\
                     +"/" + self.__DeviceID
        self.message = {"Topic": self.topic , "ClientID":self.ClientID,
                            "INFO":{"Type":self.val_type , "Value":None , "Time":'',
                            "Unit":'Celsius'}}


        self.client = MyMQTT(self.ClientID, self.broker, self.port, None)


    def start(self)-> None : 
        self.client.start()

    def stop(self)-> None: 
        self.client.stop()

    def publish(self, value)-> None: 
        logging.info("Moisture value is: " + str(value))
        self.message["INFO"]["Time"] = str('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
        self.message["INFO"]["Value"] = value 
        self.client.myPublish(self.topic, self.message)

if __name__ == "__main__": 
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    # open info.json and get User ID and Plant ID
    with open("info.json", "r") as f: 
        info = json.load(f)
        UserID = info["User_ID"]
        PlantID = info["Plant_ID"]
        f.close()
    UserID = "user"+str(UserID)     
    PlantID = "plant1"+str(PlantID)
    DeviceID =  "device1"
    temperature = device_connector_temp( UserID, PlantID, DeviceID)
    temperature.start()
    """  Finish the LAST part """
    
    logging.info(" Temperature Connector is activated \n")
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
            

   