from gettext import Catalog
import json
from urllib.error import HTTPError 
import cherrypy
from datetime import datetime
from Statistics.stats_moisture import record_moist
from Statistics.stats_temperature import record_temp
from Statistics.stats_humidity import record_humidity
import os 
import logging
from .Scale import Scaler



class CatalogManager:
     
    def __init__(self):
        self.stats_temp = record_temp()
        self.stats_humidity = record_humidity()
        self.stats_moisture = record_moist()
        PATH = os.path.dirname(os.path.abspath(__file__))
        self.Catalog_path= os.path.join(PATH, "catalog.json")
    
    def GET(self,*uri,**params):
        if len(uri)!= 0 and uri[0] == 'Catalog':
            with open(self.Catalog_path) as json_file:
                catalog = json.load(json_file)
                json_file.close()

            if uri[1] == "mqtt_details":
                details = {}
                details['broker'] = catalog["broker"]
                details['port'] = catalog['port']
                return json.dumps(details)
            
            elif uri[1] == "ThinkSpeak": 
                user = uri[2]
                plant = uri[3]
                details = {}
                details = catalog["ThinkSpeak Field"]
                return json.dumps(details)
                


            elif uri[1] == "topics":
                # get the corresponding topic from  Catalog.json of corresponding program and type and user 
                program = params["program"]
                Val_type = params['type']
                user = uri[2]
                plant = uri[3]

                for _user in catalog['Users']:
                    if int(user[-1]) == _user['ID']:
                        if plant in catalog['Users'][user]["Plants"]:
                            if program in _user["Plants"][plant]['topics']:
                                for  _plant in _user["Plants"]: 
                                    if _plant["ID"] == int(plant[-1]): 
                                        if Val_type in _plant['topics'][program]:
                                            logging.info("Topic found for %s and %s" %(program, Val_type))
                                            return json.dumps({"topic":_plant['topics'][program][Val_type]}) 
                                        else: 
                                            return cherrypy.HTTPError(400, f"Topic not found for {program} and {Val_type}")
                            else : 
                                return cherrypy.HTTPError(400, f"Topic not found for {program} and {Val_type}")
                    else : 
                        continue 


            elif uri[1] =="user_info":
                user = dict()               
                id = int(uri[2][-1])
                for _user in catalog['Users']:
                    if id == _user['ID']:
                        user["name"] = _user["Name"]
                        user["ID"] = _user["ID"]
                        logging.info("Irrigation status found for %s and %s" %(user))
                        return json.dumps(user)   
               
                return cherrypy.HTTPError(400, f"User not found")
                
           
            elif uri[1] == "Irrigation_Status":
                user = uri[2]
                plant = uri[3]
                for _user in catalog['Users']:
                    if _user["ID"] == int(user[-1]):
                        for _plant in _user["Plants"]:
                            if _plant["ID"] == int(plant[-1]):
                                logging.info("Irrigation status found for %s and %s" %(user, plant))
                                return json.dumps({"Irrigation status":_plant["Irrigation"]})
                
                return cherrypy.HTTPError(400, f"Error")
          
          
            elif uri[1] == "Health_Status":
                user = uri[2]
                plant = uri[3]
                for _user in catalog['Users']:
                    if _user["ID"] == int(user[-1]):
                        for _plant in _user["Plants"]:
                            if _plant["ID"] == int(plant[-1]):
                                logging.info("Irrigation status found for %s and %s" %(user, plant))
                                return json.dumps({"Health status":_plant["Health Status"]})
                 
                return cherrypy.HTTPError(400, f"Error")
                
               
            elif uri[1] == "ChatBot": 
                user = uri[2]
                plant = uri[3]
                for _user in catalog['Users']:
                    if _user["ID"] == int(user[-1]):
                        for _plant in _user["Plants"]:
                            if _plant["ID"] == int(plant[-1]):
                                logging.info("Irrigation status found for %s and %s" %(user, plant))
                                return json.dumps({"Chatbot":_plant["ChatBot"]})
            else : 
                cherrypy.HTTPError(400, "Bad Catalog Request")
                

        else : 
            return cherrypy.HTTPError(400, "Bad Get Request")    
                    
    
    def POST(self,*uri,**param):

        body = cherrypy.request.body.read()
        Input = json.load(body)

    
        if len(uri)!= 0 and uri[0] == "irrigation" : 
            with open("Catalog.json",'w+') as json_file : 
                catalog = json.loads(json_file)
                json_file.close()
                user = param["user"]
                plant =  param["plant"]
            last_update =  datetime.strptime(catalog["Users"][user]["Plants"][plant]["irrigation"]["time"],'%m/%d/%y %H:%M:%S')
            new_update = datetime.strptime(Input["time"],'%m/%d/%y %H:%M:%S')
            if last_update.day ==  new_update.day :              
                catalog["Users"][user]["Plants"][plant]["irrigation"]["Number of irrigation This day"] += 1
            else : 
                catalog["Users"][user]["Plants"][plant]["irrigation"]["Number of irrigation This day"] = 1
            catalog["Users"][user]["Plants"][plant]["irrigation"]["duration"] = Input["duration"]  
            with open("catalog_test.json", "w") as json_file:
                json.dump(catalog, json_file, indent=4)
                json_file.close()
                
        elif len(uri) != 0 and uri[0] =="health" : 
            with open("Catalog.json") as json_file : 
                catalog = json.loads(json_file)
                json_file.close()
            user = param["user"]
            plant = param["plant"]
            catalog["Users"][user]["Plants"][plant]["health data"]["health status"] = Input["health"]
            catalog["Users"][user]["Plants"][plant]["health data"]["Last Update"] = Input["time"]
            with open("catalog_test.json", "w") as json_file:
                json.dump(catalog, json_file, indent=4)
                json_file.close()
                
        else : 
            return cherrypy.HTTPError(400, "Bad Post Request")
    
    def PUT(self,*uri,**param):
        body = cherrypy.request.body.read()
        Input = json.load(body)
        Sca = Scaler()
        if len(uri)!= 0 and uri[0] == "add_user": 
            Sca.add_user(Input)
            return "User added"
        if len(uri)!= 0 and uri[0] == "add_plant": 
            user_ID=param["user"]
            Sca.add_folder()
            Sca.add_plant(Input,user_ID)
            return "Plant added"
    def DELETE(self,*uri, **param): 
        Sca = Scaler()
        if len(uri)!= 0 and uri[0] == "delete_user": 
            user_ID=param["user"]
            Sca.delete_user(user_ID)
            return "User deleted"
        if len(uri)!= 0 and uri[0] == "delete_plant": 
            user_ID=param["user"]
            plant_ID=param["plant"]
            Sca.delete_plant(user_ID,plant_ID)
            return "Plant deleted"
        
           
   
                

         
                

                
if __name__=="__main__":

    conf={
        '/':{
                'request.dispatch':cherrypy.dispatch.MethodDispatcher()
        }
    }
    cherrypy.config.update({
        'server.socket_host': '127.0.0.1', 'server.socket_port': 8080
    })
    webapp= CatalogManager()
    cherrypy.tree.mount(webapp,'/',conf)
    cherrypy.engine.start()
    cherrypy.engine.block()


    
                

            