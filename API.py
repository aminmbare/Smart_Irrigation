from gettext import Catalog
import json
from urllib.error import HTTPError 
import cherrypy
from datetime import datetime
from Statistics.stats_moisture import record_moist
from Statistics.stats_temperature import record_temp
from Statistics.stats_humidity import record_humidity
import os 




class CatalogManager:
     
    def __init__(self):
        self.stats_temp = record_temp()
        self.stats_humidity = record_humidity()
        self.stats_moisture = record_moist()
        PATH = os.getcwd()
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
                details = {}
                details = catalog["ThinkSpeak Field"]
                return json.dumps(details)
                


            elif uri[1] == "topics":
                program = params["program"]
                Val_type = params['type']


                if Val_type in Catalog['topics'][program]:
                        return json.dumps({"topic":catalog['topics'][program][Val_type]}) 
                else : 
                    return cherrypy.HTTPError(400, f"Topic not found for {program} and {Val_type}")


            elif uri[1] =="users_info":
                user = dict()
                user['Name'] = Catalog["User_Name"]
                user['ID'] = Catalog["User_ID"]
                return json.dumps(user)

            elif uri[1] == "Irrigation_Status":
                return json.dumps({"health status":Catalog["Plants"]["Irrigation"]})
          
          
            elif uri[1] == "Health_Status":
                   return json.dumps({"health status":Catalog["Plants"]["health data"]})
               
            elif uri[1] == "ChatBot": 
                return json.dumps({"ChatBot":Catalog["ChatBot"]})
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

    
        if len(uri) != 0 and uri[0] == "statistics" :
            with open("stats.json") as json_file : 
                stats = json.load(json_file)
                json_file.close()

            timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            # Adding Temperature , Humidity , Moisture , Health and Irrigation Data to Stats
            if uri[1] == "Temperature": 
                stats["Temperature"].append({"t":str(timestamp) , "v": str(Input["value"])})
            
            if uri[1] == "Moisture": 
                stats["Moisture"].append({"t":str(timestamp) , "v": str(Input["value"])})
            if uri[1] == "Humidity" : 
                stats["Humidity"].append({"t":str(timestamp) , "v": str(Input["value"])})    
            if uri[1] == "Health" : 
                stats["Health"].append({"t":str(timestamp) , "v": str(Input["value"])})    
            if uri[1] == "Irrigation": 
                stats["Irrigation"].append({"t":str(timestamp) , "v": str(Input["value"])})    
            File = open("stats.json", "w+") 
            File.write(json.dumps(stats, indent = 4))
            File.close()
        elif len(uri)!= 0 and uri[0] == "irrigation" : 
            with open("Catalog.json") as json_file : 
                catalog = json.loads(json_file)
                json_file.close()
            
            last_update =  datetime.strptime(catalog["Plants"]["irrigation"]["time"],'%m/%d/%y %H:%M:%S')
            new_update = datetime.strptime(Input["time"],'%m/%d/%y %H:%M:%S')
            if last_update.day ==  new_update.day : 
                
                catalog["Plants"]["irrigation"]["Number of irrigation This day"] += 1
            else : 
                catalog["Plants"]["irrigation"]["Number of irrigation This day"] = 1
            catalog["Plants"]["irrigation"]["duration"] = Input["duration"]  
            File = open("stats.json", "w+") 
            File.write(json.dumps(stats, indent = 4))
            File.close()
        elif len(uri) != 0 and uri[0] =="health" : 
            with open("Catalog.json") as json_file : 
                catalog = json.loads(json_file)
                json_file.close()
            catalog["Plants"]["health data"]["health status"] = Input["health"]
            catalog["Plants"]["health data"]["Last Update"] = Input["time"]
            File = open("stats.json", "w+") 
            File.write(json.dumps(stats, indent = 4))
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


    
                

            