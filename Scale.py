import logging 
import datetime 
import time
import json 
import os 
import shutil
import telepot
from  telepot.loop import MessageLoop
import hashlib
#  Upon receiving a request to add a user or plant for a user 
# this class will modifify catalog.json file 
# and create a new folder for the user or plant contained the device connector and controllers
class Scaler(object):
    def __init__(self,bot_token: str)-> None:
            path = os.path.dirname(os.path.abspath(__file__))
            #open device_connector_temp of user 1
            # open MyMQTT of user 1
            self.bot = telepot.Bot(bot_token)
            MessageLoop(self.bot, {'registration': self.registation}).run_as_thread()
            with open(os.path.join(path,"MyMQTT.py"), "r") as f:
                self.MyMQTT = f.read()
                f.close()
            with open (os.path.join(path, "Connectors", "user_1", "plant_1", "Device_Connector_temperature.py"), "r") as f:
                self.device_connector_temperature = f.read()
                f.close()
            #open device_connector_humidity of user 1
            with open (os.path.join(path, "Connectors", "user_1", "plant_1", "Device_Connector_humidity.py"), "r") as f:
                self.device_connector_humidity = f.read()
                f.close()
            #open device_connector_moisture of user 1
            with open (os.path.join(path, "Connectors", "user_1", "plant_1", "Device_Connector_moisture.py"), "r") as f:
                self.device_connector_moisture = f.read()
                f.close()
            # open irrigation controller of user 1
            with open (os.path.join(path, "Controllers", "user_1","plant_1", "Irrigation_Controller.py"), "r") as f:
                self.irrigation_controller = f.read()
                f.close()
            #open heathing controller of user 1
            with open (os.path.join(path, "Controllers", "user_1","plant_1", "Health_Controller.py"), "r") as f:
                self.heath_controller = f.read()
                f.close()
            with open (os.path.join(path, "Connectors", "user_1", "plant_1", "info.json"), "r") as f:
                self.info = json.load(f)
                f.close()
            # open abstract class of device connector
            with open(os.path.join("Connectors", "user_1", "plant_1","Abstract_Device_Connector.py"), "r") as f:
                self.abstract_device_connector = f.read()
                f.close()
            # open abstract class of device controller
            with open (os.path.join(path, "Controllers", "user_1","plant_1", "Controller.py"), "r") as f:
                self.abstract_device_controller = f.read()
                f.close()
            # Connectors path
            self.connector_path = os.path.join(path, "Connectors")
            # Controllers path
            self.controller_path = os.path.join(path, "Controllers")
            self.Connector_list = [(self.device_connector_humidity,"Device_Connector_humidity.py"), (self.device_connector_moisture,"Device_Connector_moisture.py"), (self.device_connector_temperature,"Device_Connector_temperature.py"),(self.abstract_device_connector,"Abstract_Device_Connector.py"),(self.MyMQTT,"MyMQTT.py")]
            self.Controller_list = [(self.irrigation_controller,"Irrigation_Controller.py"), (self.heath_controller,"Heating_Controller.py"),(self.MyMQTT,"MyMQTT.py"),(self.abstract_device_controller,"Controller.py")]

    def add_user(self,dictionary : dict)-> None: 
        # add user to catalog 
        with open("catalog.json", "r") as f:
            catalog = json.load(f)
            f.close()
        self.ID = len(catalog["Users"])+1
        self.catalog["Users"][self.ID] =dictionary
        # create a new folder for the user 
        new_user_path_connector = os.path.join(self.connector_path,f"user_{self.ID}")
        new_user_path_controller = os.path.join(self.controller_path,f"user_{self.ID}" )
        os.mkdir(new_user_path_connector)
        os.mkdir(new_user_path_controller)           
        # update catalog 
        logging.info("NEXT STEP , TELEGRAM BOT USER REGISTRATION")

        while not self.registration_over : 
            time.sleep(5)
        with open("catalog.json", "w+") as f:  
            json.dump(self.catalog, f,indent=4)
            f.close()    
          
    def registration(self, msg): 
        content_type, chat_type, chat_ID = telepot.glance(msg)
        message = msg['text']
        if message == "/start":
            self.bot.sendMessage(chat_ID, text=f"Welcome user {self.ID} to the Smart Garden Bot")
            self.bot.sendMessage(chat_ID, text="For the registration please send me your account password : /password <your password>")
        elif message.startswith("/password"):
            password =message.split(" ")[1]
            hash_object = hashlib.sha256(password.encode())
            hash_password = hash_object.hexdigest()
            self.catalog["Users"][self.ID]["ChatBot"]["Password"] = hash_password
            self.catalog["Users"][self.ID]["ChatBot"]["Chat_ID"] = chat_ID
            
            self.bot.deleteMessage((chat_ID, msg["message_id"]))
            self.bot.sendMessage(chat_ID, text="You have successfully registered to the Smart Garden Bot")
            self.registration_over = True
            
    def add_folder(self, user_key : str)-> bool:
        with open("catalog.json", "r") as f:
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
        return True
    def add_plant(self,user_key: str,dictionary : dict)-> bool:
        
        # add plant to catalog
        with open("catalog.json", "r") as f:
            catalog = json.load(f)
            f.close()
        
        plant_key = len(catalog["Users"][user_key]["Plants"]) +1

        logging.info("User key is: %s", user_key)
        if user_key in catalog["Users"]:
            catalog["Users"][user_key]["Plants"][f"plant_{plant_key}"] = dictionary
        else : 
            return False 
 
        
        
        connector_path = os.path.join(self.connector_path, f"user_{user_key}")
        logging.info("Connector path is: %s", connector_path)   
        new_plant_path_connector = os.path.join(connector_path, f"plant_{plant_key}")
        
        controller_path = os.path.join(self.controller_path, f"user_{user_key}")
        logging.info("Controller path is: %s", controller_path)   
        new_plant_path_controller = os.path.join(controller_path, f"plant_{plant_key}")

        for file , file_name in self.Connector_list:
            logging.info(f"File {file_name} is being added to the Connector folder for user {user_key} ")
            with open(os.path.join(new_plant_path_connector, file_name), "w") as f:
                f.write(file)
                f.close()
            with open(os.path.join(new_plant_path_connector, "info.json"), "w") as f:
                    self.info["Plant_ID"] = f"plant_{plant_key}"
                    self.info["User_ID"] = f"user_{user_key}"
                    json.dumps(self.info)
                    f.close()
        for file , file_name in self.Controller_list:
                logging.info(f"File {file_name} is being added to the Controller folder for user {user_key} ")
                with open(os.path.join(new_plant_path_controller, file_name), "w") as f:
                    f.write(file)
                    f.close()
                with open(os.path.join(new_plant_path_controller, "info.json"), "w") as f:
                    self.info["Plant_ID"] = f"plant_{plant_key}"
                    self.info["User_ID"] = f"user_{user_key}"
                    json.dumps(self.info,indent =4 )
                    f.close()
        with open("catalog.json", "w+") as f:
            json.dump(catalog, f,indent= 4)
            f.close()   
        return True
    def delete_user(self, user_key : str)-> bool:
        # delete user from catalog
        with open("catalog.json", "r") as f:
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
        # update catalog
        with open("catalog.json", "w+") as f:
            json.dump(catalog, f)
            f.close()
    def delete_plant(self, user_key : str, plant_key : str)-> bool:
        # delete plant from catalog
        with open("catalog.json", "r") as f:
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
        # update catalog
        with open("catalog.json", "w+") as f:
            json.dump(catalog, f,indent = 4)
            f.close()
        return True
        
        
        
        

        
                
                    