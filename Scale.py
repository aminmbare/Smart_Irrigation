import logging 
import datetime 
import json 
import os 

#  Upon receiving a request to add a user or plant for a user 
# this class will modifify catalog.json file 
# and create a new folder for the user or plant contained the device connector and controllers
class Scaler(object):
    def __init__(self,dictionary: dict)-> None:
            path = os.path.dirname(os.path.abspath(__file__))
            self.dictionary = dictionary 
            #open catalog 
            with open("catalog.json", "r") as f: 
                self.catalog = json.load(f)
                f.close()
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
        
    def add_user(self)-> None: 
        # add user to catalog 
        new_user_id = "user"+str(len(self.catalog["Users"]))
        ID = self.dictionary["User_ID"]
        self.catalog["Users"][new_user_id]= self.dictionary
        number_of_plants = len(self.dictionary["Plants"])
        # create a new folder for the user 
        new_user_path = os.path.join(self.connector_path,f"user_{ID}")
        os.mkdir(new_user_path)
        for i in range(number_of_plants):
            new_plant_path = os.path.join(new_user_path, f"plant_{i+1}")
            os.mkdir(new_plant_path)
        # create a new folder for the user 
        new_user_path = os.path.join(self.controller_path, self.dictionary["User_ID"])
        os.mkdir(new_user_path)
        # update catalog 
        with open("catalog.json", "w+") as f: 
            json.dump(self.catalog, f)
            f.close()      
    
    def add_plant(self,num_plants : int,ID: int,flag : bool )-> None:

            if flag : 
                old_plants = len(self.catalog["Users"][f"user{ID}"]["Plants"])
                for new_plant_id in self.dictionary:

                    self.catalog["Users"][f"user_{ID}"]["Plants"][new_plant_id] = self.dictionary[new_plant_id]
                with open("catalog.json", "w+") as f: 
                    logging.info("Catalog is being updated")
                    json.dump(self.catalog, f)
                    f.close() 
            else : 
                old_plants = 0
            path = os.path.join(self.connector_path, f"user_{ID}")
            logging.info("Controller path is: %s", path)
            for i in range(num_plants): 
                new_plant_path = os.path.join(path, f"plant_{old_plants+i+1}")
                os.mkdir(new_plant_path)
                for file , file_name in self.Connector_list:
                    logging.info(f"File {file_name} is being added to the Connector folder for user {ID} ")
                    with open(os.path.join(new_plant_path, file_name), "w") as f:
                        f.write(file)
                        f.close()
                with open(os.path.join(new_plant_path, "info.json"), "w") as f:
                    self.info["Plant_ID"] = f"plant_{i+1+old_plants}"
                    self.info["User_ID"] = f"user_{ID}"

                    json.dumps()
                    f.close()
            path = os.path.join(self.controller_path, f"user_{ID}")
            
            logging.info("Controller path is: %s", path)
            for i in range(num_plants): 
                new_plant_path = os.path.join(path, f"plant_{i+1}")
                os.mkdir(new_plant_path)
                for file , file_name in self.Controller_list:
                    logging.info(f"File {file_name} is being added to the Controller folder for user {ID} ")
                    with open(os.path.join(new_plant_path, file_name), "w") as f:
                        f.write(file)
                        f.close()
                with open(os.path.join(new_plant_path, "info.json"), "w") as f:
                    json.dumps(self.info)
                    f.close()   
                
                    