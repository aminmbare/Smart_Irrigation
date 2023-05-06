from abc import ABC , abstractmethod
import requests 
import json 
class device_connector(ABC): 
    def __init__(self)-> None: 
        mqtt_details = json.loads(requests.get('http://127.0.0.1:8080/catalog/mqtt_details'))
        self.port =  int(mqtt_details["port"])
        self.broker =  mqtt_details["broker"]
    @abstractmethod
    def start(self)-> None : 
        pass 
    @abstractmethod
    def stop(self)-> None : 
        pass 
    @abstractmethod
    def publish(self)-> None: 
        pass 