import json
with open("catalog_test.json") as json_file:
                catalog = json.load(json_file)
                json_file.close()
program = "controller"
Val_type = "temperature"
user = "user_1"     
plant = "plant_1"      
if user in catalog['Users']:
                    if plant in catalog['Users'][user]["Plants"]:
                        if program in catalog['Users'][user]["Plants"][plant]['topics']:
                            if Val_type in catalog['Users'][user]["Plants"][plant]['topics'][program]:
                                print("aaa")
                