from abc import ABC , abstractclassmethod 
import requests
import os
import json
from cryptography.fernet import Fernet
class controller(ABC): 
    def __init__(self) -> None:
        local_path = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(local_path,"configs.json"),"r") as f: 
            configs = json.load(f)
            f.close()
        self.catalog_address = configs["Catalog"]["ip_address"]
        self.catalog_port =  int(configs["Catalog"]["port"])
        self.mqtt_port =  int(configs["MQTT"]["port"])
        self.broker =  configs["MQTT"]["broker"]
        self.health_port = configs["Health_Server"]["port"]
        self.health_address = configs["Health_Server"]["ip_address"]   
        self.key = configs["Encryption_key"].encode('utf-8')   
        ## topics 
        self.temperature_topic = configs["MQTT"]["topics"]["Sensor"]["temperature"]
        self.moisture_topic = configs["MQTT"]["topics"]["Sensor"]["moisture"]
        self.image_topic = configs["MQTT"]["topics"]["Sensor"]["image"]  
        self.valve_topic = configs["MQTT"]["topics"]["actuator"]["irrigation"]
    @abstractclassmethod
    def start(self)-> None: 
        pass 
    @abstractclassmethod
    def subscribe(self)-> None: 
        pass 
    @abstractclassmethod
    def stop(self)-> None : 
        pass
    @abstractclassmethod 
    def notify(self)-> None : 
        pass 
    def encryptdat(self,msg:dict): 
        f = Fernet(self.key)
        return f.encrypt(json.dumps(msg).encode())
    def decryptdat(self,msg:bytes): 
        f = Fernet(self.key)
        return json.loads(f.decrypt(msg).decode())



