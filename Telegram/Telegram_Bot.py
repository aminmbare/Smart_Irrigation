

import telepot 
from  telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

import requests
import datetime
import time
import MyMQTT
## make a telegram bot that informs the user about the health status of the plant
## the bot is able to switch on/off the irrigation system
import logging
class SwitchBot:
    def __init__(self,token :str ) -> None:
        self.tokenBot = token
        self.bot = telepot.Bot(self.tokenBot)
        mqtt_details = (requests.get('http://127.0.0.1:8080/catalog/mqtt_details')).json()

        self.__ClientID = "telegramBot"
        self.client = MyMQTT(self.__ClientID,mqtt_details["broker"],mqtt_details["port"],None)
        self.client.start()
        self._ValueType = "irrigation"
        self._unit = "boolean"
        MessageLoop(self.bot, {'Menu': self.available_service,'chat': self.on_chat_message, 'callback_query': self.on_callback_query}).run_as_thread()
    
    def publish(self,value,topic)-> None : 
        message = {"Topic": topic , "ClientID":self.__ClientID,
                            "INFO":{"Type":self.__ValueType , "Value":value , "Time":str('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())),
                            "Unit":self.__unit}}

        self.client.MyPublish(topic, message)    
    
    def authentication(self,message:str,chat_ID)-> None : 
        usernumber = message.split(" ")[1]
        password = message.split(" ")[2]
        
        _pass=requests.get(f'http://127.0.0.1:8080/catalog/ChatBot?usernumber={usernumber}').jsom()
        if password == _pass["Password"]:
                self.verify = True
                self.bot.sendMessage(chat_ID, text="You are now logged in as Please select one of the following services:")
                self.bot.sendMessage(chat_ID, text="""- /irrigation_switch : Irrigate your plant \n
                             - /health_status : Check the health status of your plant \n
                             - /irrigation_status : Check the irrigation status of your plant \n    
                             - /logout : Logout from the bot \n    
                             """, reply_markup=self.available_service())
                self.user = usernumber
                self.catalog = requests.get(f'http://127.0.0.1:8080/catalog/user_info?usernumber={usernumber}').jsom()
        else : 
                self.bot.sendMessage(chat_ID, text="Wrong password")
        
    def on_message_chat(self,msg): 
        content_type, chat_type, chat_ID = telepot.glance(msg)
        message = msg['text']
        
        if message == "/start":
            self.bot.sendMessage(chat_ID, text="Welcome to the Smart Garden Bot")
            self.bot.sendMessage(chat_ID,text = "Please insert your user number and password with the following format: \n /login username password")
        
        if message.startswith("/login") and self.verify: 
            self.authentication(message)
            self.bot.sendMessage(chat_ID, text="""- /irrigation_switch/plant_ID : Irrigate your plant \n
                                 - /health_status/plant_ID : Check the health status of your plant \n
                                 - /irrigation_status/plant_ID : Check the irrigation status of your plant \n        
                                 """, reply_markup=self.available_service())
        
        if message.startswith("/irrigation_switch") and self.verify:
            buttons = [[InlineKeyboardButton(text=f'ON', callback_data=f'on'),
                        InlineKeyboardButton(text=f'OFF', callback_data=f'off')]]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            self.bot.sendMessage(chat_ID, text='What do you want to do', reply_markup=keyboard)
            self.plant = message[-1]
            
        if message.startswith("/health_status") and self.verify:
            health_status =(requests.get(f'http://127.0.0.1:8080/catalog/Health_Status?user={self.user}&plant={message[-1]}').json())
            self.bot.sendMessage(chat_ID, text=f"plant number {message[-1]} is {health_status['health_status']}  Last Update was on {health_status['Last_Update']}")
        
        if message.startswith("/irrigation_status"):
            irrigation_status =(requests.get(f'http://127.0.0.1:8080/catalog/Irrigation_Status?user={self.user}&plant={message[-1]}').json())
            self.bot.sendMessage(chat_ID, text=f"Time of Irrigation {irrigation_status['time']} , Duration of Irrigation {irrigation_status['duration']}, Number of Irrigations This day {irrigation_status['Number of irrigation This day']}")
        else:
            self.bot.sendMessage(chat_ID, text="Command not supported")     
        
        if message == "/logout" and self.verify:
            self.verify = False
            self.user = None 
            self.bot.sendMessage(chat_ID, text="You are now logged out")
    def on_callback_query(self,msg):
        query_ID , chat_ID , query_data = telepot.glance(msg,flavor='callback_query')
        topic = requests.get(f'http://127.0.0.1:8080/catalog/topics?user={self.user}&plant={self.plant}&program=actuator&type=irrigation').json()
        if query_data == "On":
            self.send_actuation(True,topic)
    
    def send_actuation(self,value:bool,topic: str)-> None :
        self.publish(value,topic)
        
        
        
if __name__ == "__main__":
    token = (requests.get('http://127.0.0.1:8080/catalog/ChatBot_token').json())["ChatBot"]
    sb=SwitchBot(token)
    while True:
        time.sleep(3)
        

    
               
        
        
        
        
        
        