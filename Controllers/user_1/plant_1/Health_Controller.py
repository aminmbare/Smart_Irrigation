from MyMQTT import *
import datetime
import requests 
from tensorflow import keras
from Abstract_Device_Controller import controller
import time 
import logging 
import json
import pickle
from PIL import Image
import os

class Controller_health(controller): 
    def __init__(self,UserID : str , PlantID : str )->None: 
        super(Controller_health,self).__init__()
        self._UserID = "user"+UserID 
        self._PlantID = "plant"+PlantID 
        self._ClientID = "Controller_health"+"_"+self._UserID +"_"+ self._PlantID
        self._client = MyMQTT(self._ClientID,self.broker,self.port,self)
        
    def start(self)-> None:
        self._client.start()
    def stop(self)-> None : 
        self._client.stop() 
    
    def subscribe(self): 
        topic = (requests.get(f'http://127.0.0.1:8080/Catalog/topics?user={self._UserID[-1]}&plant={self._PlantID[-1]}&program=Sensor&type=image').json())["topic"] 
        self._client.mySubscribe(topic)
        
    def notify(self, topic, msg)-> None : 
        message = json.loads(msg)
        image = message["INFO"]["Value"]
        health = self.fetch_from_cloud()
        
        requests.post(f'http://127.0.0.1:8080/health?user={self._UserID[-1]}&plant={self._PlantID[-1]}',json.dumps(health))
        

    def fetch_from_cloud(self):
        logging.info("Image has been captured by the controller, Ready to send it to the cloud")
        name_img_1 = "/Users/aminembarek/Desktop/IOT-PROJECT/images/tomato.jpeg"
        image = keras.utils.load_img(name_img_1, target_size=(800, 800))
        Serialized = pickle.dumps(image, protocol=pickle.DEFAULT_PROTOCOL)
        files = {'image': (name_img_1, Serialized, 'multipart/form-data', {'Expires': '0'})}
        resp = requests.post('http://44.211.155.225:8000/leaf_detection',files = files)
        image = Image.fromarray(pickle.loads(resp.content))
        image = image.resize((224,224))
        logging.info("Leaf Detection Worked Succesfully")
        name_img = "disease_detection.jpg"
        Serialized = pickle.dumps(image, protocol=pickle.DEFAULT_PROTOCOL)
        files = {'image': (name_img, Serialized, 'multipart/form-data', {'Expires': '0'})}
        resp = requests.post('http://44.211.155.225:8000/leaf_disease',files = files)
        health_status = resp.json()
        
        logging.info(f"leaf disease detection Worked Succesfully, the response was {health_status}")
        requests.post(f'http://127.0.0.1:8080/health?user={self._UserID[-1]}&plant={self._PlantID[-1]}',json.dumps(health_status))

    
if __name__ == "__main__":
    CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
    Info_path = os.path.join(CURRENT_PATH, "info.json")
    logging.basicConfig(level = logging.INFO)
    with open(Info_path, "r") as f: 
        info = json.load(f)
        UserID = info["User_ID"]
        PlantID = info["Plant_ID"]
        f.close()
    
    
    controller  = Controller_health(UserID,PlantID)
    controller.start()
    controller.subscribe()
    while True  : 
        controller.fetch_from_cloud()
        time.sleep(60)
        
    
        
        
        

        
        
        
    
    