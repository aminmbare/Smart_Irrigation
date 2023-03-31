import json 
import requests
import datetime
url=  "https://api.thingspeak.com/update.json"

data_upload = json.dumps({
            "api_key": 'MV7B8DSLUNAL5ZMX',
            "channel_id": '2090142',
            "created_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "entry_id": 0,
            "field1": 25,
            "field2": 25,
            "field3": 25,



        })
headers = {'Content-type': 'application/json', 'Accept': 'raw'}

requests.post(url=url, data=data_upload,headers=headers)