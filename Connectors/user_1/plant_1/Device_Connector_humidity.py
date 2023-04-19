from MyMQTT import * 
import datetime 
import logging
import time 
import random 
import Abstract_Device_Connector



class device_connector_humidity(Abstract_Device_Connector): 

    def __init__(self , UserID : int, PlantID: int , DeviceID: int)-> None: 
        super().__init__()
        self.__root = "IOT_PROJECT" 
        self.__UserID = UserID 
        self.__PlantID = PlantID 
        self.__DeviceID = DeviceID
        self.val_type = "humidity"
        self.ClientID = "Humidity_Connector_"+self.__UserID+"_"+self.__PlantID+"_"+self.__DeviceID
        self.topic = self.__root +"/"+ self.__UserID +"/" + self.__PlantID+"/"+self.val_type\
                     +"/" + self.__DeviceID
        self.message = {"Topic": self.__topic , "ClientID":self.ClientID,
                            "INFO":{"Type":self.val_type , "Value":None , "Time":'',
                            "Unit":'%'}}


        self.client = MyMQTT(self.ClientID, self.broker, self.port, None)
        


    def start(self)-> None: 
        self.client.start()

    def stop(self)-> None: 
        self.client.stop()

    def publish(self, value) -> None: 
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
    PlantID = "plant"+str(PlantID)
    DeviceID =  "device3"
    humidity = device_connector_humidity(UserID, PlantID, DeviceID)
    humidity.start()
    logging.info(" Moisture Connector is active\n")
    """  Finish the LAST part """
    while True : 
        i = 80
        while i<= 95 : 
            temp = i
            humidity.publish(temp)
            i = random.choice([0,1,0.5])
            time.sleep(4)
        while i >= 50: 
            temp = i 
            humidity.publish(temp)
            i -= random.choice([0,1,0.5])
            time.sleep(4)
    
