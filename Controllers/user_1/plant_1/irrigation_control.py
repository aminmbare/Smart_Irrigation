import MyMQTT
import datetime 
import requests 
import numpy as np 
import tensorflow as tf
import pickle 
import Controller
import time 
import logging 
import json



class Controller_Irrigation(Controller):
    def __init__(self,UserID: str, PlantID: str)-> None:
        super().__init__()
        self.__ClientID = "Controller_irrigation"
        self.__UserID = UserID 
        self.__PlantID = PlantID 

        self.ClienID = "Controller_irrigation"+"_"+self.__UserID +"_"+ self.__PlantID 
        self.__temperature = 0
        self.__moisture = 0
        self.__temperature_state = False 
        self.__moisture_state = False 
        self.client = MyMQTT(self.ClientID, self.broker, self.port,None)
        self.ValueType = "Irrigation" 

        self.message = {"Topic": "" , "ClientID":self.__ClientID,
                            "INFO":{"Type":self.ValueType , "Value":None , "Time":str('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())),
                            "Unit":'On/Off'}}
    def start(self)-> None:
        self.client.start()
    def publish(self,value,topic)-> None : 
        self.message["INFO"]["value"]= value
        self.client.MyPublish(topic, self.message)
        

    def subscribe(self): 
        temperature_topic = (requests.get(f'http://127.0.0.1:8080/catalog/{self.__UserID}/{self.__PlantID}/all_topics?program=Sensor&type=temperature').json())["topic"]
        moisture_topic = (requests.get(f'http://127.0.0.1:8080/catalog/{self.__UserID}/{self.__PlantID}/all_topics?program=Sensor&type=moisture').json())["topic"]
        self.__topics = [(temperature_topic,0),(moisture_topic,1)]
        self.client.MySubscribe(self.__topics)
    def stop(self): 
        self.client.stop()
    def notify(self,topic,msg):        
        if topic == "IOT_PROJECT/user1/plant1/temperature/device1" and not self.__temperature_state :
                self.__temperature_state = True 
                self.__temperature = msg["INFO"]["Value"]
        if topic == "IOT_PROJECT/user1/plant1/moisture/device2" and not self.__moisture_state: 
                self.__moisture_state = True 
                self.__moisture = msg["INFO"]["Value"]
        if self.__moisture_state and self.__temperature_state : 
                if self.irrigation_decision(self.__temperature,self.__moisture): 
                    time = self.irrigation_time(self.__moisture)
                    logging.info(f"Irrigation system is On for {time} s")
                    self.send_actuation(True)
                    self.__moisture_state , self.__temperature_state = False , False 
                    requests.post('http://127.0.0.1:8080/irrigation',json.dumps({"duration":time,"time":datetime.datetime.now().strftime("%m/%d/%y %H:%M:%S")}))  
                    
        time.sleep(120.0)            
    @staticmethod               
    def irrigation_decision(temperature,moisture)-> int: 
        _input = np.array([[moisture, temperature]])
        irrigation = tf.keras.models.load_model("irrigation_decision.h5")
        result = irrigation.predicts(_input)
        return round(result)

    @staticmethod
    def irrigation_time(moisture)-> float :
        file_name = "Linear_regression_model.pkl"
        loaded_model = pickle.load(open(file_name,"rb"))
        result = loaded_model.predict(moisture)
        return result
    
    def send_actuation(self,value:bool)-> None :
        
        new_topic = requests.get("http://127.0.0.1:8000/catalog/all_topics?program=controllers&type=irrigation").json()["topic"]
        self.publish(value,new_topic[0])
        
    
if __name__ == "__main__":
    with open("info.json", "r") as f: 
        info = json.load(f)
        UserID = info["User_ID"]
        PlantID = info["Plant_ID"]
        f.close()
    UserID = "user"+str(UserID)      
    PlantID = "plant"+str(PlantID)
    
    controller  = Controller_Irrigation(UserID,PlantID)
    controller.start()
    controller.subscribe()
    while True  : 
        time.sleep(3)
        
    
    

        
