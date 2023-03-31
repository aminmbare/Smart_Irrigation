from gettext import Catalog
import json
from urllib.error import HTTPError 
import cherrypy
from datetime import datetime
from Statistics.stats_moisture import record_moist
from Statistics.stats_temperature import record_temp
from Statistics.stats_humidity import record_humidity




class CatalogManager:
     
    def __init__(self):
        self.stats_temp = record_temp()
        self.stats_humidity = record_humidity()
        self.stats_moisture = record_moist()
    
    def GET(self,*uri,**params):
        if len(uri)!= 0 and uri[0] == 'Catalog':
            with open('catalog.json') as json_file:
                catalog = json.load(json_file)
                json_file.close()

            if uri[1] == "mqtt_details":
                details = {}
                details['broker'] = catalog["broker"]
                details['port'] = catalog['port']
                return json.dumps(details)


            if uri[1] == "topics":
                program = params["program"]
                Val_type = params['type']
                topics = []
                for user in Catalog['Users_List']:
                    if Val_type in Catalog["Users_List"][user]['topics'][program]:
                        topics.append(catalog["Users_List"][user]['topics'][program][Val_type])
                return json.dumps({"topic":topics}) 


            if uri[1] =="users_info":
                user = []
                try: 
                    user['Name'] = Catalog["User_info"]["User_Name"]
                    user['ID'] = Catalog["User_info"]["User_ID"]
                    return json.dumps(user)
                except : 
                    raise cherrypy.HTTPError(500,"Request Not Valid")
            if uri[1] == "Plant_Info":
                plant = []
                plant = Catalog["User_info"]["Plant_Info"]                 
                return json.dumps(plant)
          
          
            if uri[1] == "Health_Status":
                   return json.dumps({"health status":Catalog["User_Ino"]["Plant_info"]["health status"]})

        elif len(uri) != 0 and uri[0] == 'statistics' : 
            with open("catalog.json") as json_file: 
                catalog = json.load(json_file)
                json_file.close()

            with open("stats.json") as json_file: 
                stats = json.load(json_file)
                json_file.close()
            
            temp_stats = self.stats_temp(uri[0], uri[1],stats["Temperature"])
            moist_stats = self.stats_moisture(uri[0], uri[1],stats["Moisture"])    
            humidity_stats = self.stats_humidity(uri[0], uri[1],stats["Humidity"])

            return json.dumps({"temperature": temp_stats, "Moisture":moist_stats , "Humidity":humidity_stats})

        else : 
            return "Not Valid Command , Try Again !!"    
                    
            
            
            """
            CHATBOT POST MISSING 
            STATISTIC MISSING 
            
            """
    def POST(self,*uri,**param):

        body = cherrypy.request.body.read()

        Input = json.load(body)

        if len(uri) != 0 and uri[0] == "catalog" : 
            if uri[1] =="ChatID":
                """
                CHAT ID POST
                """

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
        if len(uri)!= 0 and uri[0] == "irrigation" : 
            with open("Catalog.json") as json_file : 
                catalog = json.loads(json_file)
                json_file.close()
            
            last_update =  datetime.strptime(catalog["userLists"]["Plants"]["irrigation"]["time"],'%m/%d/%y %H:%M:%S')
            new_update = datetime.strptime(Input["time"],'%m/%d/%y %H:%M:%S')
            if last_update.day ==  new_update : 
                catalog["userLists"]["Plants"]["irrigation"]["Number of irrigation This day"] += 1
            else : 
                catalog["userLists"]["Plants"]["irrigation"]["Number of irrigation This day"] = 1
            catalog["userLists"]["Plants"]["irrigation"]["duration"] = Input["duration"]  
            File = open("stats.json", "w+") 
            File.write(json.dumps(stats, indent = 4))
            File.close()
        if len(uri) != 0 and uri[0] =="health" : 
            with open("Catalog.json") as json_file : 
                catalog = json.loads(json_file)
                json_file.close()
            catalog["userLists"]["Plants"]["health data"]["health status"] = Input["health"]
            catalog["userLists"]["Plants"]["health data"]["Last Update"] = Input["time"]
            File = open("stats.json", "w+") 
            File.write(json.dumps(stats, indent = 4))
            File.close()
            
             
                
                        

    def PUT(self, *uri , **params):

        if len(uri) != 0 and uri[0] =="catalog": 
            with open("catalog.son") as json_file: 
                catalog = json.load(json_file)
                json_file.close()

            if uri[1] == "threshold_moisture" : 
                user = uri[1]
                plant = uri[2]
                threshold_min = params["threshold_min"]
                threshold_max = params["threshold_max"]  
                catalog["userList"]["user"]["Plants"][plant]["Min_Moisture"] = threshold_min     
                catalog["userList"]["user"]["Plants"][plant]["Max_Moisture"] = threshold_max


            #if uri[1] == "Irrigation Status":
            #    user = uri[1]
            #    plant = uri[2]
            #    duration = params["duration"]
            #    time = params["time"]
            #    rep = params["reps"]
            #    catalog["userList"]["user"]["Plants"][plant]["irrigation"]["time"] = time
            #    catalog["userList"]["user"]["Plants"][plant]["irrigation"]["duration"] = duration
            #    if rep : 
            #        catalog["userList"]["user"]["Plants"][plant]["irrigation"]["Number of irrigation This day"]+=1
            #    else : 
            #        catalog["userList"]["user"]["Plants"][plant]["irrigation"]["Number of irrigation This day"] = 0
                

                
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



                

            