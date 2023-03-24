from abc import ABC , abstractclassmethod 
import requests

class Statistics(ABC): 
    def __init__(self) -> None:
        mqtt_details = (requests.get('http://127.0.0.1:8080/catalog/mqtt_details')).json()
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