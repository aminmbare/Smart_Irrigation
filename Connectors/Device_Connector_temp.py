from MyMQTT import * 
import datetime 
import requests 
import time 
import random 
import Abstract_Device_Connector
import logging


class device_connector_temp(Abstract_Device_Connector): 

    def __init__(self , broker: str, port:int, UserID:int, PlantID: int , DeviceID: int )-> None: 
        super().__init__("temperature","°C","TemperatureSensor")
        self.__root = "IOT_PROJECT"
        self.__UserID = UserID 
        self.__PlantID = PlantID 
        self.__DeviceID = DeviceID 
        self.__broker = broker 
        self.__port = port
        self.__topic = self.__root +"/"+ self.__UserID +"/" + self.__PlantID+"/"+self.val_type\
                     +"/" + self.__DeviceID
        self.__message = {"Topic": self.__topic , "ClientID":self.ClientID,
                            "INFO":{"Type":self.val_type , "Value":None , "Time":'',
                            "Unit":self.unit}}


        self.client = MyMQTT(self.ClientID, self.__broker, self.__port, None)


    def start(self)-> None : 
        self.client.start()

    def stop(self)-> None: 
        self.client.stop()

    def publish(self, value)-> None: 

        self.__message["INFO"]["Time"] = str('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
        self.__message["INFO"]["Value"] = value 
        self.client.myPublish(self.topic, self.__message)

if __name__ == "__main__": 

    mqtt_details = (requests.get('http://127.0.0.1:8080/catalog/mqtt_details')).json()
    broker = mqtt_details["broker"]
    port = int(mqtt_details['port'])
    UserID = "user1"       
    PlantID = "plant1"
    DeviceID =  "device1"
    temperature = device_connector_temp(broker, port, UserID, PlantID, DeviceID)
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
            

   