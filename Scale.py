import logging 
import datetime 
import json 
import os 
import shutil


#  Upon receiving a request to add a user or plant for a user 
# this class will modifify catalog.json file 
# and create a new folder for the user or plant contained the device connector and controllers
class Scaler(object):
    def __init__(self)-> None:
            path = os.path.dirname(os.path.abspath(__file__))
            #open device_connector_temp of user 1
            
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
            with open (os.path.join(path, "Controllers", "user_1","plant_1", "Heating_Controller.py"), "r") as f:
                self.heath_controller = f.read()
                f.close()
            with open (os.path.join(path, "Connectors", "user_1", "plant_1", "info.json"), "r") as f:
                self.info = json.load()
                f.close()
            # Connectors path
            self.connector_path = os.path.join(path, "Connectors")
            # Controllers path
            self.controller_path = os.path.join(path, "Controllers")
            self.Connector_list = [(self.device_connector_humidity,"Device_Connector_humidity.py"), (self.device_connector_moisturemoisture,"Device_Connector_moisture.py"), (self.device_connector_temperature,"Device_Connector_temperature.py")]
            self.Controller_list = [(self.irrigation_controller,"Irrigation_Controller.py"), (self.heath_controller,"Heating_Controller.py")]

    def add_user(self,dictionary : dict)-> None: 
        # add user to catalog 
        with open("catalog.json", "r") as f:
            catalog = json.load(f)
            f.close()
        ID = dictionary["User_ID"]
        catalog["Users"].append(dictionary)
        # create a new folder for the user 
        new_user_path_connector = os.path.join(self.connector_path,f"user_{ID}")
        new_user_path_controller = os.path.join(self.controller_path,f"user_{ID}" )
        os.mkdir(new_user_path_connector)
        os.mkdir(new_user_path_controller)           
        # update catalog 
        with open("catalog.json", "w+") as f: 
            json.dump(catalog, f)
            f.close()      
    def add_folder(self, ID : int):
        with open("catalog.json", "r") as f:
            catalog = json.load(f)
            f.close()
        for _user in catalog["Users"]:
            if _user["User_ID"] == ID:
                User__Catalog = _user
                break
        number_of_plants = len(User__Catalog["Plants"])
        
        new_plant_path_connector = os.path.join(self.connector_path,f"user_{ID}", f"plant_{number_of_plants+1}")
        os.mkdir(new_plant_path_connector)
        new_plant_path_controller = os.path.join(self.controller_path,f"user_{ID}", f"plant_{number_of_plants+1}")
        os.mkdir(new_plant_path_controller)
    
    def add_plant(self,ID: int,dictionary : dict)-> None:
        # add plant to catalog
        with open("catalog.json", "r") as f:
            catalog = json.load(f)
            f.close()
        for _user in catalog["Users"]:
            if _user["User_ID"] == ID:
                _user["Plants"].append(dictionary)
                break
            
        plant_id = dictionary["Plant_ID"]
        
        path = os.path.join(self.connector_path, f"user_{ID}")
        logging.info("Controller path is: %s", path)
    
        new_plant_path = os.path.join(path, f"plant_{plant_id}")

        for file , file_name in self.Connector_list:
            logging.info(f"File {file_name} is being added to the Connector folder for user {ID} ")
            with open(os.path.join(new_plant_path, file_name), "w") as f:
                f.write(file)
                f.close()
            with open(os.path.join(new_plant_path, "info.json"), "w") as f:
                    self.info["Plant_ID"] = f"plant_{plant_id}"
                    self.info["User_ID"] = f"user_{ID}"
                    json.dumps()
                    f.close()
        for file , file_name in self.Controller_list:
                logging.info(f"File {file_name} is being added to the Controller folder for user {ID} ")
                with open(os.path.join(new_plant_path, file_name), "w") as f:
                    f.write(file)
                    f.close()
                with open(os.path.join(new_plant_path, "info.json"), "w") as f:
                    self.info["Plant_ID"] = f"plant_{plant_id}"
                    self.info["User_ID"] = f"user_{ID}"
                    json.dumps()
                    f.close()
    def delete_user(self, ID : int)-> None:
        # delete user from catalog
        with open("catalog.json", "r") as f:
            catalog = json.load(f)
            f.close()
        for _user in catalog["Users"]:
            if _user["User_ID"] == ID:
                catalog["Users"].remove(_user)
                break
        # delete user folder
        path = os.path.join(self.connector_path, f"user_{ID}")
        shutil.rmtree(path)
        path = os.path.join(self.controller_path, f"user_{ID}")
        shutil.rmtree(path)
        # update catalog
        with open("catalog.json", "w+") as f:
            json.dump(catalog, f)
            f.close()
        
        
        

        
                
                    