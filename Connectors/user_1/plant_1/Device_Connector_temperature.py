from MyMQTT import * 
import datetime 
import requests 
import time 
from  Abstract_Device_Connector import device_connector
import logging


class device_connector_temp(device_connector): 

    def __init__(self , UserID:int, PlantID: int ,TS : dict )-> None: 
        super(device_connector_temp,self).__init__()
        self._root = "IOT_PROJECT"
        self._UserID = "user"+UserID 
        self._PlantID = "plant"+PlantID 
        self._DeviceID = "device1"
        self._val_type = "temperature"
        self._ClientID = "Temperature_Connector"+"_"+self._UserID+"_"+self._PlantID+"_"+self._DeviceID
        self._topic = (requests.get(f'http://127.0.0.1:8080/Catalog/topics?user={self._UserID[-1]}&plant={self._PlantID[-1]}&program=Sensor&type=temperature').json())["topic"]
        logging.info(self._topic)
        self._message = {"Topic": self._topic , "ClientID":self._ClientID,
                            "INFO":{"Type":self._val_type , "Value":None , "Time":'',
                            "Unit":'Celsius'}}


        self.client = MyMQTT(self._ClientID, self.broker, self.port, None)

        self._TS = TS
        self._count = 0
    def start(self): 
        self.client.start()

    def stop(self): 
        self.client.stop()
 

    def publish(self, value)-> None: 
        logging.info("Temperature value is: " + str(value))
        self._message["INFO"]["Time"] = str('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
        self._message["INFO"]["Value"] = value 
        self.client.myPublish(self._topic, self._message)
        # Upload to ThingSpeak
        data_upload = json.dumps({
            "api_key": self._TS["api key"],
            "channel_id": self._TS["channel_id"],
            "created_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "entry_id": self._count,
            "field1":  value,      
        })
        self._count +=1
        headers = {'Content-type': 'application/json', 'Accept': 'raw'}
        requests.post(url=self._TS["url"], data=data_upload, headers=headers)
        logging.info("Temperature value has been upload to ThingSpeak: " + str(value))
if __name__ == "__main__": 
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    # open info.json and get User ID and Plant ID
    with open("info.json", "r") as f: 
        info = json.load(f)
        UserID = info["User_ID"]
        PlantID = info["Plant_ID"]
        f.close()
    # open ThingSpeak.json and get ThingSpeak info
    ThinkSpeak = requests.get(f"http://127.0.0.1:8080/Catalog/ThingSpeak?user={UserID}&plant={PlantID}").json()
    temperature = device_connector_temp(UserID, PlantID,ThinkSpeak)
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
            

   