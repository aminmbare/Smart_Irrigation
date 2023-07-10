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
    """
    This class manages the health of the plant ,
    it subscribes to the image topic and sends the picture of the plant to the a health inspection microservice
    running on the cloud, the microservice in cloud  returns the health status of the plant 
    WARNING : This class will not work ,  unless you have the health inspection microservice running on the cloud
    """
    def __init__(self,UserID : str , PlantID : str )->None: 
        super(Controller_health,self).__init__()
        self._UserID = "user"+UserID 
        self._PlantID = "plant"+PlantID 
        self._ClientID = "Controller_health"+"_"+self._UserID +"_"+ self._PlantID
        self._client = MyMQTT(self._ClientID,self.broker,self.mqtt_port,self)

    def start(self)-> None:
        self._client.start()
    def stop(self)-> None : 
        self._client.stop() 
    
    def subscribe(self): 
        #topic = (requests.get(f'http://{self.catalog_address}:{self.catalog_port}/Catalog/topics?user={self._UserID[-1]}&plant={self._PlantID[-1]}&program=Sensor&type=image').json())["topic"] 
        self._client.mySubscribe(self.image_topic)
        
    def notify(self, topic, msg)-> None : 
        message = json.loads(msg)
        image = message["INFO"]["Value"]
        health = self.request_cloud()
        
        requests.post(f'http://127.0.0.1:8080/health?user={self._UserID[-1]}&plant={self._PlantID[-1]}',json.dumps(health))
        

    def request_cloud(self):
        logging.info("Image has been captured by the controller, Ready to send it to the cloud")
        #image_path  = "/Users/aminembarek/Desktop/IOT-PROJECT/images/tomato.jpeg"
        image_path =  os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','..','images','tomato.jpeg'))
        image = keras.utils.load_img(image_path, target_size=(800, 800))
        Serialized = pickle.dumps(image, protocol=pickle.DEFAULT_PROTOCOL)
        files = {'image': (image_path, Serialized, 'multipart/form-data', {'Expires': '0'})}
        resp = requests.post(f'http://{self.health_address}:{self.health_port}/leaf_detection',files = files)
        image = Image.fromarray(pickle.loads(resp.content))
        image = image.resize((224,224))
        logging.info("Leaf Detection Worked Succesfully")
        name_img = "disease_detection.jpg"
        Serialized = pickle.dumps(image, protocol=pickle.DEFAULT_PROTOCOL)
        files = {'image': (name_img, Serialized, 'multipart/form-data', {'Expires': '0'})}
        resp = requests.post(f'http://{self.health_address}:{self.health_port}/leaf_disease',files = files)
        health_status = resp.json()
    
        logging.info(f"leaf disease detection Worked Succesfully, the response was {health_status}")
        requests.put(f'http://127.0.0.1:8080/health?user={self._UserID[-1]}&plant={self._PlantID[-1]}',json.dumps(health_status))

    
if __name__ == "__main__":
    CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
    Info_path = os.path.join(CURRENT_PATH, "configs.json")
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
        controller.request_cloud()
        time.sleep(60)
        
    
        
        
        

        
        
        
    
    