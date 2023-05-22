import MyMQTT 
import datetime
import requests 
import tensorflow as tf 
from Abstract_Device_Controller import Controller
import time 
import logging 
import json
import pickle
from PIL import Image
import os

class Controller_health(Controller): 
    def __init__(self,UserID : str , PlantID : str )->None: 
        super(Controller_health,self).__init__()
        
        self.__UserID = UserID
        self.__PlantID = PlantID
        self._ClientID = "Controller_health"+"_"+self._UserID +"_"+ self._PlantID
        self._client = MyMQTT(self.__ClientID,self.broker,None)
    def start(self)-> None:
        self._client.start()
    def stop(self)-> None : 
        self._client.stop() 
    
    def subscribe(self): 
        topic = (requests.get(f'http://127.0.0.1:8080/catalog/{self.__UserID}/{self.__PlantID}/all_topics?program=Sensor&type=camera').json())["topic"] 
        self.client.MySubscribe(topic)
        
    def notify(self, topic, msg)-> None : 
        message = json.loads(msg)
        image = message["INFO"]["Value"]
        time = message["INFO"]["time"]
        health = self.fetch_from_cloud()
        requests.post('http://127.0.0.1:8080/health',json.dumps(health))
        
        

    @staticmethod
    def fetch_from_cloud():
        logging.info("Image has been captured by the controller, Ready to send it to the cloud")
        name_img_1 = "leaf_detection.jpg"
        Serialized = pickle.dumps(image, protocol=pickle.DEFAULT_PROTOCOL)
        files = {'image': (name_img_1, Serialized, 'multipart/form-data', {'Expires': '0'})}
        logging.info("Leaf Detection Worked Succesfully")
        resp = requests.post('http://127.0.0.1:5000/leaf_detection',files = files)
        image=  Image.fromarray(pickle.loads(resp.content))
        image = image.resize((224,224))
        name_img = "disease_detection.jpg"
        Serialized = pickle.dumps(image, protocol=pickle.DEFAULT_PROTOCOL)
        files = {'image': (name_img, Serialized, 'multipart/form-data', {'Expires': '0'})}
        resp = requests.post('http://127.0.0.1:5000/leaf_disease',files = files)
        health_status = resp.json()
        logging.info(f"leaf disease detection Worked Succesfully, the response was {health_status}")
        return health_status
    
if __name__ == "__main__":
    CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
    Info_path = os.path.join(CURRENT_PATH, "info.json")
    with open(Info_path, "r") as f: 
        info = json.load(f)
        UserID = "user"+info["User_ID"]
        PlantID = "plant"+info["Plant_ID"]
        f.close()
    
    
    controller  = Controller_health(UserID,PlantID)
    controller.start()
    controller.subscribe()
    while True  : 
        time.sleep(3)
        
    
        
        
        

        
        
        
    
    