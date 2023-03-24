from MyMQTT import * 
import datetime 
import requests 
import time 
import random 
import Abstract_Device_Connector
import logging


class device_connector_moisture(Abstract_Device_Connector): 

    def __init__(self , broker, port, UserID, PlantID, DeviceID): 
        super().__init__("moisture","%",'MoistureSensor')
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


    def start(self): 
        self.client.start()

    def stop(self): 
        self.client.stop()

    def publish(self, value): 

        self.__message["INFO"]["Time"] = str('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
        self.__message["INFO"]["Value"] = value 
        self.client.myPublish(self.topic, self.__message)

if __name__ == "__main__": 

    mqtt_details = (requests.get('http://127.0.0.1:8080/catalog/mqtt_details')).json()
    broker = mqtt_details["broker"]
    port = int(mqtt_details['port'])
    UserID = "user1"       
    PlantID = "plant1"
    DeviceID =  "device2"
    moisture = device_connector_moisture(broker, port, UserID, PlantID, DeviceID)
    moisture.start()
    logging.info("Moisture Connector is active\n")
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