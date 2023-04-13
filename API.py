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

                if user in catalog['Users']:
                    if plant in catalog['Users'][user]["Plants"]:
                        if program in catalog['Users'][user]["Plants"][plant]['topics']:
                            if Val_type in catalog['Users'][user]["Plants"][plant]['topics'][program]:
                                logging.info("Topic found for %s and %s" %(program, Val_type))
                                return json.dumps({"topic":catalog['Users'][user]['topics']["Plants"][plant][program][Val_type]}) 
                            else: 
                                return cherrypy.HTTPError(400, f"Topic not found for {program} and {Val_type}")
                        else : 
                            return cherrypy.HTTPError(400, f"Topic not found for {program} and {Val_type}")
                    


            elif uri[1] =="user_info":
                user = dict()
                if uri[2] in Catalog["Users"]:  
                        user["name"] = Catalog["Users"][uri[2]]["Name"]
                        user["ID"] = Catalog["Users"][uri[2]]["ID"]
                        logging.info("Irrigation status found for %s and %s" %(user))
                        return json.dumps(user)   
                else : 
                    return cherrypy.HTTPError(400, f"User not found")
                
           
                                    
                

            elif uri[1] == "Irrigation_Status":
                user = uri[2]
                plant = uri[3]
                if plant in Catalog["Users"][user]["Plants"]:
                    logging.info("Irrigation status found for %s and %s" %(user, plant))
                    return json.dumps({"Irrigation status":Catalog["Users"][user]["Plants"][plant]["Irrigation"]})
                else : 
                    return cherrypy.HTTPError(400, f"Plant not found")
          
          
            elif uri[1] == "Health_Status":
                user = uri[2]
                plant = uri[3]
                if plant in Catalog["Users"][user]["Plants"]:
                    logging.info("health status found for %s and %s" %(user, plant))
                    return json.dumps({"Irrigation status":Catalog["Users"][user]["Plants"][plant]["health data"]})
                else : 
                    return cherrypy.HTTPError(400, f"Plant not found")
                
               
            elif uri[1] == "ChatBot": 
                user = uri[2]
                plant = uri[3]
                if plant in Catalog["Users"][user]["Plants"]:
                    logging.info("ChatBot found for %s and %s" %(user, plant))
                    return json.dumps({"ChatBot":Catalog["Users"][user]["Plants"][plant]["ChatBot"]})
                else : 
                    cherrypy.HTTPError(400, f"Plant not found")
            else : 
                cherrypy.HTTPError(400, "Bad Catalog Request")
                

        elif len(uri) != 0 and uri[0] == 'statistics' : 
            with open("catalog.json") as json_file: 
                catalog = json.load(json_file)
                json_file.close()

            with open() as json_file: 
                stats = json.load(json_file)
                json_file.close()
            
            temp_stats = self.stats_temp(uri[0], uri[1],stats["Temperature"])
            moist_stats = self.stats_moisture(uri[0], uri[1],stats["Moisture"])    
            humidity_stats = self.stats_humidity(uri[0], uri[1],stats["Humidity"])

            return json.dumps({"temperature": temp_stats, "Moisture":moist_stats , "Humidity":humidity_stats})

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
            catalog["Plants"]["irrigation"]["duration"] = Input["duration"]  
            File = open("stats.json", "w+") 
            File.write(json.dumps(catalog, indent = 4))
            File.close()
        elif len(uri) != 0 and uri[0] =="health" : 
            with open("Catalog.json") as json_file : 
                catalog = json.loads(json_file)
                json_file.close()
            user = param["user"]
            plant = param["plant"]
            catalog["Plants"]["health data"]["health status"] = Input["health"]
            catalog["Plants"]["health data"]["Last Update"] = Input["time"]
            File = open("stats.json", "w+") 
            File.write(json.dumps(catalog, indent = 4))
            File.close()
        else : 
            return cherrypy.HTTPError(400, "Bad Post Request")
            
             
                

         
                

                
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


    
                

            