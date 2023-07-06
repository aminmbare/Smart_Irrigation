import logging 
import datetime 
import time
import json 
import os 
import shutil
from cryptography.fernet import Fernet


class Scaler(object):
    """Upon receiving a request to add a user or plant for a user , this class will modifify catalog.json file
    and create a new folder for the user or plant contained the device connector and controllers    
    """
    def __init__(self)-> None:
            path = os.path.dirname(os.path.abspath(__file__))          
            # open MyMQTT of user 1
            with open(os.path.join(path,"..", "Connectors", "user_1", "plant_1","MyMQTT.py"), "r") as f:
                self.MyMQTT = f.read()
                f.close()
            with open (os.path.join(path,"..", "Connectors", "user_1", "plant_1", "Device_Connector_temperature.py"), "r") as f:
                self.device_connector_temperature = f.read()
                f.close()
            #open device_connector_humidity of user 1
            with open (os.path.join(path,'..', "Connectors", "user_1", "plant_1", "Device_Connector_humidity.py"), "r") as f:
                self.device_connector_humidity = f.read()
                f.close()
            #open device_connector_moisture of user 1
            with open (os.path.join(path,'..', "Connectors", "user_1", "plant_1", "Device_Connector_moisture.py"), "r") as f:
                self.device_connector_moisture = f.read()
                f.close()
            # open irrigation controller of user 1
            with open (os.path.join(path,'..', "Controllers", "user_1","plant_1", "Irrigation_Controller.py"), "r") as f:
                self.irrigation_controller = f.read()
                f.close()
            #open heathing controller of user 1
            with open (os.path.join(path,'..', "Controllers", "user_1","plant_1", "Health_Controller.py"), "r") as f:
                self.heath_controller = f.read()
                f.close()
            with open (os.path.join(path,'..', "Connectors", "user_1", "plant_1", "configs.json"), "r") as f:
                self.connector_configs = json.load(f)
                f.close()
            with open (os.path.join(path,'..', "Controllers", "user_1", "plant_1", "configs.json"), "r") as f:
                self.controllers_configs = json.load(f)
                f.close()
            # open abstract class of device connector
            with open(os.path.join(path,'..',"Connectors", "user_1", "plant_1","Abstract_Device_Connector.py"), "r") as f:
                self.abstract_device_connector = f.read()
                f.close()
            
            # open abstract class of device controller
            with open (os.path.join(path,'..', "Controllers", "user_1","plant_1", "Abstract_Device_Controller.py"), "r") as f:
                self.abstract_device_controller = f.read()
                f.close()
            # open Thinkspeak of user 1
            with open(os.path.join(path,'..',"ThinkSpeak","user_1","plant_1","ThinkSpeakAdapter.py"), "r") as f:
                self.ThinkSpeak = f.read()
                f.close()
            # open config file of user 1 
            with open(os.path.join(path,'..',"ThinkSpeak","user_1","plant_1","configs.json"), "r") as f:
                self.ThinkSpeak_configs = json.load(f)
                f.close()
            # Connectors path
            self.connector_path = os.path.join(path,'..', "Connectors")
            # Controllers path
            self.controller_path = os.path.join(path,'..', "Controllers")
            self.ThinkSpeak_path = os.path.join(path,'..', "ThinkSpeak")
            self.Connector_list = [(self.device_connector_humidity,"Device_Connector_humidity.py"), (self.device_connector_moisture,"Device_Connector_moisture.py"), (self.device_connector_temperature,"Device_Connector_temperature.py"),(self.abstract_device_connector,"Abstract_Device_Connector.py"),(self.MyMQTT,"MyMQTT.py")]
            self.Controller_list = [(self.irrigation_controller,"Irrigation_Controller.py"), (self.heath_controller,"Heating_Controller.py"),(self.MyMQTT,"MyMQTT.py"),(self.abstract_device_controller,"Abstract_Device_Controller.py")]

    def add_user(self,dictionary : dict)-> None: 
        # add user to catalog 
        path = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(path,"catalog.json"), "r") as f:
            catalog = json.load(f)
            f.close()
        self.ID = len(catalog["Users"])+1
        catalog["Users"][self.ID] =dictionary
        # create a new folder for the user 
        new_user_path_connector = os.path.join(self.connector_path,f"user_{self.ID}")
        new_user_path_controller = os.path.join(self.controller_path,f"user_{self.ID}" )
        new_user_path_thinkspeak = os.path.join(self.ThinkSpeak_path,f"user_{self.ID}" )
        os.mkdir(new_user_path_connector)
        os.mkdir(new_user_path_thinkspeak)
        os.mkdir(new_user_path_controller)           
        # update catalog 
        with open(os.path.join(path,"catalog.json"), "w+") as f:  
            json.dump(catalog, f,indent=4)
            f.close()    
            
          
            
    def add_folder(self, user_key : str)-> bool:
        path = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(path,"catalog.json"), "r") as f:
            catalog = json.load(f)
            f.close()
        if user_key in catalog["Users"]:
            number_of_plants = len(catalog["Users"][user_key]["Plants"])
        else : 
            return False
        new_plant_path_connector = os.path.join(self.connector_path,f"user_{user_key}", f"plant_{number_of_plants+1}")
        os.mkdir(new_plant_path_connector)
        new_plant_path_controller = os.path.join(self.controller_path,f"user_{user_key}", f"plant_{number_of_plants+1}")
        os.mkdir(new_plant_path_controller)
        new_plant_path_think_speak= os.path.join(self.ThinkSpeak_path,f"user_{user_key}", f"plant_{number_of_plants+1}")
        os.mkdir(new_plant_path_think_speak)
        return True
    def add_plant(self,user_key: str,dictionary : dict)-> bool:
        def get_topics(user_id : int, plant_id: int)->  dict: 
            topics = dict()
            base_topic = f"IOT_PROJECT/user{user_id}/plant{plant_id}"
            topics["actuator"]= {"irrigation":base_topic+"/irrigation/device5"}
            topics["Sensor"]={"temperature":  base_topic+"/temperature/device1","moisture":base_topic+"/moisture/device2",
                                             "humidity":base_topic+"/humidity/device3","image":base_topic+"/image/device4"}

            return topics
        def set_catalog_topics(dictioary: dict,user_id,plant_id)-> dict : 
            measures = ["temperature", "moisture", "humidity","image", "irrigation"]
            base_topic = f"IOT_PROJECT/user{user_id}/plant{plant_id}"
            for m in measures: 
                for keys , values in dictioary["Devices"].items():
                    if m in values["Measure_Type"]:
                        values["Available_Service"]["MQTT"]["topic"] = base_topic+f"/{m}"
            return dictioary         
        path = os.path.dirname(os.path.abspath(__file__))
        # add plant to catalog
        with open(os.path.join(path,"catalog.json"), "r") as f:
            catalog = json.load(f)
            f.close()
        
        plant_key = len(catalog["Users"][user_key]["Plants"]) +1

        logging.info("User key is: %s", user_key)
        if user_key in catalog["Users"]:
            catalog["Users"][user_key]["Plants"][plant_key] = set_catalog_topics(dictionary,user_key,plant_key)
        else : 
            return False 
 
        
        connector_path = os.path.join(self.connector_path, f"user_{user_key}")
        logging.info("Connector path is: %s", connector_path)   
        new_plant_path_connector = os.path.join(connector_path, f"plant_{plant_key}")
        
        controller_path = os.path.join(self.controller_path, f"user_{user_key}")
        logging.info("Controller path is: %s", controller_path)   
        new_plant_path_controller = os.path.join(controller_path, f"plant_{plant_key}")
        thinkspeak_path = os.path.join(self.ThinkSpeak_path, f"user_{user_key}")
        new_plant_path_thinkspeak = os.path.join(thinkspeak_path, f"plant_{plant_key}")
        
        encryption_key = Fernet.generate_key().decode("utf-8")
        ## set up  the Connectors scripts, such as temperature, moisture and humidity connectors
        for file , file_name in self.Connector_list:
            logging.info(f"File {file_name} is being added to the Connector folder for user {user_key} ")
            with open(os.path.join(new_plant_path_connector, file_name), "w") as f:
                f.write(file)
                f.close()
        ## set the the configuration file for the connectors
        with open(os.path.join(new_plant_path_connector, "configs.json"), "w") as f:
                self.connector_configs["Plant_ID"] = str(plant_key)
                self.connector_configs["User_ID"] = str(user_key)
                self.connector_configs["Encryption_key"] = encryption_key
                self.connector_configs["MQTT"]["topics"] = get_topics(user_key,plant_key)
                
                json.dump(self.connector_configs,f,indent = 4)
                f.close()
        ## set the controller scripts , such as health and irrigation controller 
        for file , file_name in self.Controller_list:
                logging.info(f"File {file_name} is being added to the Controller folder for user {user_key} ")
                with open(os.path.join(new_plant_path_controller, file_name), "w") as f:
                    f.write(file)
                    f.close()
        with open(os.path.join(new_plant_path_controller, "configs.json"), "w") as f:
            self.controllers_configs["Plant_ID"] = str(plant_key)
            self.controllers_configs["User_ID"] = str(user_key)
            self.controllers_configs["Encryption_key"] = encryption_key
            self.controllers_configs["MQTT"]["topics"] = get_topics(user_key,plant_key)
            json.dump(self.controllers_configs,f,indent =4 )
            f.close()
        with open(os.path.join(new_plant_path_thinkspeak, "ThinkSpeakAdapter.py"), "w") as f:
            f.write(self.ThinkSpeak)
            f.close()
        with open(os.path.join(new_plant_path_thinkspeak,"MyMQTT.py"), "w") as f:
            f.write(self.MyMQTT)
            f.close() 
        with open(os.path.join(new_plant_path_thinkspeak, "configs.json"), "w") as f:
            self.ThinkSpeak_configs["Plant_ID"] = str(plant_key)
            self.ThinkSpeak_configs["User_ID"] = str(user_key)
            self.ThinkSpeak_configs['ThinkSpeak_Field'] = dictionary['ThinkSpeak_Field']
            self.ThinkSpeak_configs["Encryption_key"] = encryption_key
            self.ThinkSpeak_configs["MQTT"]["topics"] = get_topics(user_key,plant_key)
            logging.info(self.ThinkSpeak_configs)
            json.dump(self.ThinkSpeak_configs,f,indent = 4)
            f.close()

        # update catalog
        with open(os.path.join(path,"catalog.json"), "w+") as f:
            json.dump(catalog, f,indent= 4)
            f.close()   
        return True
    def delete_user(self, user_key : str)-> bool:
        # delete user from catalog
        path = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(path,"catalog.json"), "r") as f:
            catalog = json.load(f)
            f.close()
        if user_key in catalog["Users"]:
                # remove user from catalog         
            del catalog["Users"][user_key]
        else:
            return False 
        # delete user folder
        path = os.path.join(self.connector_path, f"user_{user_key}")
        shutil.rmtree(path)
        path = os.path.join(self.controller_path, f"user_{user_key}")
        shutil.rmtree(path)
        path = os.path.join(self.ThinkSpeak_path, f"user_{user_key}")
        shutil.rmtree(path)
        # update catalog
        path = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(path,"catalog.json"), "w+") as f:
            json.dump(catalog, f,indent=4)
            f.close()
    def delete_plant(self, user_key : str, plant_key : str)-> bool:
        # delete plant from catalog
        path = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(path,"catalog.json"), "r") as f:
            catalog = json.load(f)
            f.close()
        if user_key in catalog["Users"]:
                if  plant_key in catalog["Users"][user_key]["Plants"]:
                    # remove plant from catalog
                    del catalog["Users"][user_key]["Plants"][plant_key]
                else:
                    return False 
        else:
            return False 
        # delete plant folder
        path = os.path.join(self.connector_path, f"user_{user_key}", f"plant_{plant_key}")
        shutil.rmtree(path)
        path = os.path.join(self.controller_path, f"user_{user_key}", f"plant_{plant_key}")
        shutil.rmtree(path)
        path = os.path.join(self.ThinkSpeak_path, f"user_{user_key}", f"plant_{plant_key}")
        shutil.rmtree(path)
        # update catalog
        path = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(path,"catalog.json"), "w+") as f:
            json.dump(catalog, f,indent = 4)
            f.close()
        return True
        
        
        
        

        
                
                    