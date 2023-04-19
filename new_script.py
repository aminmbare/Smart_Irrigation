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

if "2" in catalog["Users"]:
    print("User already exists")
