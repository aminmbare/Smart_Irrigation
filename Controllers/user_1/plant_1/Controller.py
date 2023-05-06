from abc import ABC , abstractclassmethod 
import requests
import json 
class controller(ABC): 
    def __init__(self) -> None:
        mqtt_details = json.loads(requests.get('http://127.0.0.1:8080/catalog/mqtt_details'))
        self.port =  int(mqtt_details["port"])
        self.broker =  mqtt_details["broker"]
        
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


