import json
#open catlog.json and add a user
with open("catalog_test.json", "r") as f:
    catalog = json.load(f)
    f.close()
user =  {
    "User_Name":"Arman",
    "ChatBot": "",
    "Plants":{}
 }

with open("catalog_test.json", "w+") as f:
    catalog["Users"]["3"] = user
    json.dump(catalog, f,indent= 4)
    f.close()