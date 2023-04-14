import json
import datetime 
with open("API.py",'r') as file:
                script = file.read()
                file.close()
                

                
with open("new_script.py",'w') as file:
                file.write(script)
                file.close()
import os 

PATH = os.path.dirname(os.path.abspath(__file__))
for i in range(2,4):
    user_path = os.path.join(PATH, "Connectors","user_1",f"plant_{i}")
    
    os.mkdir(user_path)