

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
        self.__tokenBot = token
        self.__bot = telepot.Bot(self.tokenBot)
        mqtt_details = (requests.get('http://127.0.0.1:8080/catalog/mqtt_details')).json()
        self.__irrigation_topic  = requests.get("http://127.0.0.1:8000/catalog/all_topics?program=controllers&type=irrigation").json()["topic"]
        self.__ClientID = "telegramBot"
        self.client = MyMQTT(self.__ClientID,mqtt_details["broker"],mqtt_details["port"],None)
        self.client.start()
        self.__ValueType = "irrigation"
        self.__unit = "boolean"
        MessageLoop(self.bot, {'Menu': self.available_service,'chat': self.on_chat_message, 'callback_query': self.on_callback_query}).run_as_thread()
    
    def publish(self,value,topic)-> None : 
        message = {"Topic": topic , "ClientID":self.__ClientID,
                            "INFO":{"Type":self.__ValueType , "Value":value , "Time":str('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())),
                            "Unit":self.__unit}}

        self.client.MyPublish(topic, message)    
        
    def on_message_chat(self,msg): 
        content_type, chat_type, chat_ID = telepot.glance(msg)
        message = msg['text']
        if message == "/start":
            self.bot.sendMessage(chat_ID, text="Welcome to the Smart Garden Bot")
            self.bot.sendMessage(chat_ID, text="""- /irrigation_switch : Irrigate your plant \n
                                 - /health_status : Check the health status of your plant \n
                                 - /irrigation_status : Check the irrigation status of your plant \n        
                                 """, reply_markup=self.available_service())
        if message == "/irrigation_switch":
            buttons = [[InlineKeyboardButton(text=f'ON', callback_data=f'on'),
                        InlineKeyboardButton(text=f'OFF', callback_data=f'off')]]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            self.bot.sendMessage(chat_ID, text='What do you want to do', reply_markup=keyboard)
            
        if message == "/health_status":
            health_status =(requests.get('http://127.0.0.1:8080/catalog/Health_Status').json())
            self.bot.sendMessage(chat_ID, text=f"Your plant is {health_status['health_status']}  Last Update was on {health_status['Last_Update']}")
        if message == "/irrigation_status":
            irrigation_status =(requests.get('http://127.0.0.1:8080/catalog/Irrigation_Status').json())
            self.bot.sendMessage(chat_ID, text=f"Time of Irrigation {irrigation_status['time']} , Duration of Irrigation {irrigation_status['duration']}, Number of Irrigations This day {irrigation_status['Number of irrigation This day']}")
        else:
            self.bot.sendMessage(chat_ID, text="Command not supported")     
            
    def on_callback_query(self,msg):
        query_ID , chat_ID , query_data = telepot.glance(msg,flavor='callback_query')
        if query_data == "On":
            self.send_actuation(True)
    
    def send_actuation(self,value:bool)-> None :
        self.publish(value,self.__irrigation_topic)
        
        
        
if __name__ == "__main__":
    token = (requests.get('http://127.0.0.1:8080/catalog/ChatBot').json())["ChatBot"]
    sb=SwitchBot(token)
    while True:
        time.sleep(3)
        

    
               
        
        
        
        
        
        