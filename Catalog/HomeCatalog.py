
import json
import cherrypy
from datetime import datetime
import os 
import logging
from Scale import Scaler



class CatalogManager:
     
    def __init__(self):
        PATH = os.path.dirname(os.path.abspath(__file__))
        self.Catalog_path= os.path.join(PATH, "catalog.json")
    exposed = True
    def GET(self,*uri,**params):
        if len(uri)!= 0 and uri[0] == 'Catalog':
            logging.info("Get Catalog  request open ")
            with open(self.Catalog_path) as json_file:
                logging.info("Catalog file opened")
                catalog = json.load(json_file)
                json_file.close()

            if uri[1] == "mqtt_details":
                ## not used 
                details = {}
                details['broker'] = catalog["MQTT"]["broker"]
                details['port'] = catalog["MQTT"]['port']
                return json.dumps(details)
            
            elif uri[1] == "topics":
                
                ## not used 
                # get the corresponding topic from  Catalog.json of corresponding program and type and user 
                Val_type = params['type']
                program = params['program']
                user_key = params['user']
                plant_key = params['plant']
                if user_key in catalog['Users']:
                        if plant_key in catalog['Users'][user_key]["Plants"]:
                            if program in catalog['Users'][user_key]["Plants"][plant_key]['topics']:
                                        if Val_type in  catalog['Users'][user_key]["Plants"][plant_key]['topics'][program]:
                                            logging.info("Topic found for %s and %s" %(program, Val_type))
                                            return json.dumps({"topic":catalog['Users'][user_key]["Plants"][plant_key]['topics'][program][Val_type]}) 
                                        else: 
                                            return cherrypy.HTTPError(400, f"Topic not found for {program} and {Val_type}")
                            else : 
                                return cherrypy.HTTPError(400, f"Topic not found for {program} and {Val_type}")
                        else :  
                            return cherrypy.HTTPError(400, f"Plant not found for {user_key} and {plant_key}")  
                else : 
                    return cherrypy.HTTPError(400, f"User not found for {user_key} and {plant_key}")                     

            
            ## Get the ThingSpeak Field of a plant    
            elif uri[1] == "ThingSpeak": 
                logging.debug("ThingSpeak request")
                user_key = params["user"]
                plant_key = params["plant"]
                if user_key in catalog['Users']:
                    if plant_key in catalog['Users'][user_key]["Plants"]:
                        
                        return json.dumps(catalog['Users'][user_key]["Plants"][plant_key]['ThingSpeak Field'])
                else : 
                    return cherrypy.HTTPError(400, f"User not found for {user_key} and {plant_key}")
            ## Get the irrigation status of a plant
            elif uri[1] == "Irrigation_Status":
                user_key = params["user"]
                plant_key = params["plant"]
                if user_key in catalog['Users']:
                    if plant_key in catalog['Users'][user_key]["Plants"]:
                        logging.info("Irrigation status found for %s and %s" %(user_key, plant_key))
                        return json.dumps(catalog['Users'][user_key]["Plants"][plant_key]["Irrigation_Data"])     
                return cherrypy.HTTPError(400, f"Error")
          
            ## Get the health status of a plant
            elif uri[1] == "Health_Status":
                user_key = params["user"]
                plant_key = params["plant"]
                if user_key in catalog['Users']:
                    if plant_key in catalog['Users'][user_key]["Plants"]:
                        logging.info("Health status found for %s and %s" %(user_key, plant_key))
                        return json.dumps(catalog['Users'][user_key]["Plants"][plant_key]["Health_Data"])    
                    else : 
                        cherrypy.HTTPError(400, f"Plant not found for {user_key} and {plant_key}")
                else : 
                    cherrypy.HTTPError(400, f"User not found for {user_key} and {plant_key}")
            elif uri[1] == "ChatBot_token": 
              logging.info("Chatbot token request")
              return json.dumps({"token":catalog['ChatBot_token']})     
                      
            elif uri[1] == "ChatBot": 
                user_key = params["user"]
                if user_key in catalog['Users']:

                        logging.info("Chatbot Data found for  user%s" %(user_key))
                        return json.dumps(catalog['Users'][user_key]["ChatBot"])    
                else : 
                    return json.dumps({"error":"User does not exist, Please register first by providing your data through the folling link: http://127.0.0.1:8080/add_user"})
            else : 
               return  cherrypy.HTTPError(400, "Bad Catalog Request")
                

        else :    
            return cherrypy.HTTPError(400, "Bad Get Request")    
                     
    
    def PUT(self,*uri,**param):

        body = cherrypy.request.body.read()
        logging.info(body)
        body = body.decode('utf-8')
        Input = json.loads(body)

        logging.info(Input)
        
        ## Update the irrigation status of a plant 
        if len(uri)!= 0 and uri[0] == "irrigation" : 
            with open(self.Catalog_path) as json_file : 
                catalog = json.load(json_file)
                json_file.close()

            user_key = param["user"]
            plant_key =  param["plant"]   
            try :              
                last_update =  datetime.strptime(catalog["Users"][user_key]["Plants"][plant_key]["Irrigation_Data"]["time"],'%m/%d/%y %H:%M:%S')
                new_update = datetime.strptime(Input["time"],'%m/%d/%y %H:%M:%S')
                if last_update.day ==  new_update.day :              
                    catalog["Users"][user_key]["Plants"][plant_key]["Irrigation_Data"]["Number of irrigation This day"] += 1

                else : 
                    catalog["Users"][user_key]["Plants"][plant_key]["Irrigation_Data"]["Number of irrigation This day"] = 1
                catalog["Users"][user_key]["Plants"][plant_key]["Irrigation_Data"]["duration"] = Input["duration"]  
                catalog["Users"][user_key]["Plants"][plant_key]["Irrigation_Data"]["time"] = Input["time"]
                logging.info(catalog['Users'][user_key]["Plants"][plant_key])
            except ValueError :
                catalog["Users"][user_key]["Plants"][plant_key]["Irrigation_Data"]["Number of irrigation This day"] = 1
                catalog["Users"][user_key]["Plants"][plant_key]["Irrigation_Data"]["duration"] = Input["duration"]  
                catalog["Users"][user_key]["Plants"][plant_key]["Irrigation_Data"]["time"] = Input["time"]
            with open(self.Catalog_path, "w+") as json_file:
                
                json.dump(catalog, json_file, indent=4)
                
                json_file.close()
        
        ## Update the health status of a plant  
        elif len(uri) != 0 and uri[0] =="health" : 
            with open(self.Catalog_path) as json_file : 
                catalog = json.load(json_file)
                json_file.close()
            user_key = param["user"]
            plant_key = param["plant"]
            catalog["Users"][user_key]["Plants"][plant_key]["Health_Data"]["health_status"] = Input["health"]
            catalog["Users"][user_key]["Plants"][plant_key]["Health_Data"]["Last_Update"] = Input["time"]
            with open(self.Catalog_path, "w+") as json_file:
                json.dump(catalog, json_file, indent=4)
                json_file.close()
        elif len(uri) != 0 and uri[0] =="add_chatbot_account" :
            user = param["user"] 
            with open(self.Catalog_path) as json_file :
                catalog = json.load(json_file)
                json_file.close()
            catalog["Users"][user]["ChatBot"]["ChatID"] = Input["ChatID"]
            catalog["Users"][user]["ChatBot"]["Password"] = Input["Password"]
            with open(self.Catalog_path, "w+") as json_file:
                json.dump(catalog, json_file, indent=4)
                json_file.close()
        
        else : 
            return cherrypy.HTTPError(400, "Bad Post Request")
    @cherrypy.tools.json_in()
    def POST(self,*uri,**param):
        body = cherrypy.request.json

        Sca = Scaler()
        ## add a user to catalog 
        if len(uri)!= 0 and uri[0] == "add_user": 
            logging.info(body)
            Sca.add_user(body)
            return "User added"
        ## add a plant to catalog 
        if len(uri)!= 0 and uri[0] == "add_plant": 
            user_key=param["user"]
            logging.info(body)
            if Sca.add_folder(user_key):
                if Sca.add_plant(user_key,body):
                    return "Plant added"
                else : 
                    return cherrypy.HTTPError(400, "Error")
            return cherrypy.HTTPError(400, "Error")
    
    
    def DELETE(self,*uri, **param): 
        Sca = Scaler()
        ## delete a user 
        if len(uri)!= 0 and uri[0] == "delete_user": 
            user_ID=param["user"]
            Sca.delete_user(user_ID)
            return "User deleted"
        ## delete a plant
        if len(uri)!= 0 and uri[0] == "delete_plant": 
            user_ID=param["user"]
            plant_ID=param["plant"]
            logging.info(Sca.delete_plant(user_ID,plant_ID))
            return "Plant deleted"
        
           
                
if __name__=="__main__":
    logging.basicConfig(level=logging.DEBUG,format=str('%(asctime)s - %(levelname)s - %(message)s'))
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


    
                

            