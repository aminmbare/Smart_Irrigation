from abc import ABC , abstractmethod
import requests 
import json 
import os
from cryptography.fernet import Fernet
class device_connector(ABC): 
    def __init__(self)-> None: 
        local_path = os.path.dirname(os.path.abspath(__file__))
        
        with open(os.path.join(local_path,"configs.json"),'r') as f: 
            configs = json.load(f)
            f.close()
        self.catalog_address = configs["Catalog"]["ip_address"]
        self.catalog_port =  int(configs["Catalog"]["port"])
        self.mqtt_port =  int(configs["MQTT"]["port"])
        self.broker =  configs["MQTT"]["broker"]
        self.key = configs["Encryption_key"].encode('utf-8')
        ## topics 
        self.temperature_topic = configs["MQTT"]["topics"]["Sensor"]["temperature"] 
        self.moisture_topic = configs["MQTT"]["topics"]["Sensor"]["moisture"] 
        self.humidity_topic = configs["MQTT"]["topics"]["Sensor"]["humidity"]
        
    @abstractmethod
    def start(self)-> None : 
        pass 
    @abstractmethod
    def stop(self)-> None : 
        pass 
    @abstractmethod
    def publish(self)-> None: 
        pass 
    def encryptdat(self,msg:dict): 
        f = Fernet(self.key)
        return f.encrypt(json.dumps(msg).encode()).decode("utf-8")
    def decryptdat(self,msg:bytes): 
        f = Fernet(self.key)
        return json.loads(f.decrypt(msg).decode())