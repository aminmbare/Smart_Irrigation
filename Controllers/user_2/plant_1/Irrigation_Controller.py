from MyMQTT import *
import datetime 
import requests 
import numpy as np 
import tensorflow as tf
import pickle 
from Abstract_Device_Controller import controller
import time 
import logging 
import ast
import json
import os



class Controller_Irrigation(controller):
    def __init__(self,UserID: str, PlantID: str)-> None:
        super(Controller_Irrigation,self).__init__()
        self._UserID = "user"+UserID 
        self._PlantID = "plant"+PlantID 
        
        self._ClientID = "Controller_irrigation"+"_"+self._UserID +"_"+ self._PlantID
        self._temperature = 0
        self._moisture = 0
        self._temperature_state = False 
        self._moisture_state = False 
        self.client = MyMQTT(self._ClientID, self.broker, self.mqtt_port,self)
        self.ValueType = "Irrigation" 
        self.message = {"Topic": "" , "ClientID":self._ClientID,
                            "INFO":{"Type":self.ValueType , "Value":None , "Time":str('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())),
                            "Unit":'On/Off'}}
        irrigation_model_path =  os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','..','Models','irrigation_decision.h5'))
        self.irrigation_decision_model = tf.keras.models.load_model(irrigation_model_path)
        irrigation_time_path =  os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','..','Models','Linear_regression_model.pkl'))
        self.irrigation_time_model = pickle.load(open(irrigation_time_path, 'rb'))
    def start(self)-> None:
        self.client.start()
    def publish(self,value,topic)-> None : 
        self.message["INFO"]["value"]= value
        self.client.myPublish(topic, self.message)
        
    def subscribe(self): 
        #temperature_topic = (requests.get(f'http://{self.catalog_address}:{self.catalog_port}/Catalog/topics?user={self._UserID[-1]}&plant={self._PlantID[-1]}&program=Sensor&type=temperature').json())["topic"]
        #moisture_topic = (requests.get(f'http://{self.catalog_address}:{self.catalog_port}/Catalog/topics?user={self._UserID[-1]}&plant={self._PlantID[-1]}&program=Sensor&type=moisture').json())["topic"]
        self._topics = [(self.temperature_topic,0),(self.moisture_topic,0)]
        self.client.mySubscribe(self._topics)
        
    def stop(self): 
        self.client.stop()
    def notify(self,topic,msg):        

        mydata = self.decryptdat(msg)
        logging.info(f"Message received from {topic} : {mydata}")
        if topic == self.temperature_topic and not self._temperature_state :

                self._temperature_state = True 
                self._temperature = int(mydata["INFO"]["Value"])
                logging.info(f"Temperature is {self._temperature}")

        if topic == self.moisture_topic and not self._moisture_state: 

                self._moisture_state = True 
                self._moisture = int(mydata["INFO"]["Value"])
                logging.info(f"Moisture is {self._moisture}")

        if self._moisture_state and self._temperature_state : 
                self._moisture_state , self._temperature_state = False , False 
                if self.irrigation_decision(self._temperature,self._moisture): 
                    irrigation_time = self.irrigation_time(self._moisture)
                    logging.info(f"Irrigation system is On for {time} s")
                    self.send_actuation(True)
                    requests.put(f'http://{self.catalog_address}:{self.catalog_port}/irrigation?user={self._UserID[-1]}&plant={self._PlantID[-1]}',json.dumps({"duration":irrigation_time,"time":datetime.datetime.now().strftime("%m/%d/%y %H:%M:%S")}))
                    time.sleep(30) 

    def irrigation_decision(self,temperature,moisture)-> int: 
        input = np.array([[moisture, temperature]])    
        result = self.irrigation_decision_model.predict(input)
        logging.info(f"Decision is {result}")
    
        return round(result[0,0])
    
    
    def irrigation_time(self,moisture)-> float :
        result = self.irrigation_time_model.predict([[moisture]])
        logging.info(f"Time is {result[0]}")
        return result[0][0]
    
    def send_actuation(self,value:bool)-> None :
        #new_topic = requests.get(f"http://{self.catalog_address}:{self.catalog_port}/Catalog/topics?user={self._UserID[-1]}&plant={self._PlantID[-1]}&program=actuator&type=irrigation").json()["topic"]
        self.publish(value,self.valve_topic)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
    configs_path = os.path.join(CURRENT_PATH, "configs.json")
    with open(configs_path, "r") as f: 
        configs = json.load(f)
        UserID = configs["User_ID"]
        PlantID = configs["Plant_ID"]
        f.close()


    controller  = Controller_Irrigation(UserID,PlantID)
    controller.start()
    controller.subscribe()
    while True  : 
        time.sleep(3)
        
    
    

        

