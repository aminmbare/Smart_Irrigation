from MyMQTT import * 
import datetime 
import requests 
import time 
import random 
import Abstract_Device_Connector
import logging
import os

class device_connector_moisture(Abstract_Device_Connector): 

    def __init__(self ,UserID: str,PlantID: str, DeviceID: str,**TS)-> None: 
        super().__init__()
        self._root = "IOT_PROJECT" 
        self._UserID = "user"+UserID 
        self._PlantID = "plant"+PlantID 
        self._DeviceID = "device"+DeviceID 
        self._val_type = "moisture"
        self._ClientID = "Moisture_Connector"+"_"+self._UserID+"_"+self._PlantID+"_"+self._DeviceID
        self._topic = self._root +"/"+ self._UserID +"/" + self._PlantID+"/"+self.val_type\
                     +"/" + self._DeviceID   
        
        self._message = {"Topic": self._topic , "ClientID":self._ClientID,
                            "INFO":{"Type":self.val_type , "Value":None , "Time":'',
                            "Unit":"%"}}


        self.client = MyMQTT(self.ClientID, self.broker, self.port, None)
        
        self._TS = TS
        self.count = 0
        


    def start(self): 
        self.client.start()

    def stop(self): 
        self.client.stop()

    def publish(self, value): 
        logging.info("Moisture value is: " + str(value))
        self.message["INFO"]["Time"] = str('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
        self.message["INFO"]["Value"] = value 
        self.client.myPublish(self._topic, self.message)
        # Upload to ThingSpeak
        data_upload = json.dumps({
            "api_key": self._TS["api_key"],
            "channel_id": self._TS["channel_id"],
            "created_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "entry_id": self._count,
            "field2":  value,      
        })
        self.count +=1
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
        DeviceID = info["Device_ID"]
        f.close()
    ThinkSpeak = requests.get(f"http://127.0.0.1:8080/ThingSpeak?user={UserID[-1]}&plant={PlantID[-1]} ").json()
    moisture = device_connector_moisture( UserID, PlantID, DeviceID)
    moisture.start()
    logging.info(f" Moisture Connector for {UserID}, {PlantID} , {DeviceID} is activated  ")
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