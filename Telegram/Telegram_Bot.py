

import telepot 
from  telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import hashlib
import requests
import datetime
import time
from MyMQTT import *
import json
## make a telegram bot that informs the user about the health status of the plant
## the bot is able to switch on/off the irrigation system
import logging
class SwitchBot:
    def __init__(self,token :str ) -> None:
        """
        make a telegram bot that informs the user about the health status of the plant
        the bot is able to switch on/off the irrigation system
        """
        self.bot = telepot.Bot(token)
        mqtt_details = (requests.get('http://127.0.0.1:8080/Catalog/mqtt_details')).json()
        
        self._ClientID = "telegramBot"
        self.client = MyMQTT(self._ClientID,mqtt_details["broker"],mqtt_details["port"],None)
        self.client.start()
        self._ValueType = "irrigation"
        self._unit = "boolean"
        self.verify = False
        self.plant  =None
        self.user = None
        MessageLoop(self.bot, {'chat': self.on_chat_message, 'callback_query': self.on_callback_query}).run_as_thread()
        
    def publish(self,value,topic)-> None : 
        message = {"Topic": topic , "ClientID":self._ClientID,
                            "INFO":{"Type":self._ValueType , "Value":value , "Time":str('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())),
                            "Unit":self._unit}}

        self.client.MyPublish(topic, message)    
    def authentication(self,message:str,chat_ID:str, msg_id)-> None : 
        """
        This method is used to authenticate the user to the system
        """
        usernumber = message.split(" ")[1]
        password = message.split(" ")[2]
        ## the password is hashed  before being sent to the server
        hash_object = hashlib.sha256(password.encode())
        hash_password = hash_object.hexdigest()
        _account=requests.get(f'http://127.0.0.1:8080/Catalog/ChatBot?user={usernumber}').json()
        
        logging.info("User %s is trying to log in",usernumber)
        logging.info("acount %s",_account)
        if hash_password == _account["Password"]:
                self.verify = True
                logging.info("User %s is now logged in",usernumber)
                self.bot.deleteMessage((chat_ID,msg_id))
                self.bot.sendMessage(chat_ID, text="You are now logged in , Please select you plant with the following format: \n /plant_id plantnumber")
                
                self.Chat_ID = _account["ChatID"]
                self.user = usernumber

        else : 
                self.bot.sendMessage(chat_ID, text="Wrong password or usernumber")
    def registration(self,message : str,chat_ID:str,msg_id)-> None : 
        """ 
        This method is used to register a new user to the system
        """
        check_user_exitance = requests.get(f'http://127.0.0.1:8080/Catalog/ChatBot?user={message.split(" ")[1]}').json()
        if "error" in check_user_exitance.keys():
            self.bot.sendMessage(chat_ID, text=check_user_exitance["error"])
        usernumber = message.split(" ")[1]
        password = message.split(" ")[2]
        
        hash_object = hashlib.sha256(password.encode())
        hash_password = hash_object.hexdigest()
        #_account = requests.get(f'http://127.0.0.1:8080/Catalog/ChatBot?user={usernumber}').json()
        chatbot = {"ChatID":chat_ID,"Password":hash_password}
        requests.put(f'http://127.0.0.1:8080/add_chatbot_account?user={usernumber}',json.dumps(chatbot))
        self.bot.deleteMessage((chat_ID,msg_id))
         

    def on_chat_message(self,msg): 
        content_type, chat_type, chat_ID = telepot.glance(msg)
        message = msg['text']
        logging.info("Chat ID is %s",chat_ID)
        if message.startswith("/register"):
            logging.info("User %s is trying to register",chat_ID)
            self.registration(message,chat_ID,msg["message_id"])
            self.bot.sendMessage(chat_ID,text = "You are now registered")
        elif message == "/start":
            self.bot.sendMessage(chat_ID, text="Welcome to the Smart Garden Bot")
            self.bot.sendMessage(chat_ID,text = "Please insert your user number and password with the following format: \n /login usernumber password")

 
        elif message.startswith("/login") and not self.verify: 
            self.authentication(message,chat_ID,msg["message_id"])
        elif message.startswith("/plant_id") and self.verify:
            self.plant = message.split(" ")[1]
        elif message == "/logout" and self.verify:
            self.verify = False
            self.user = None 
            self.plant = None
            self.Chat_ID = None
            self.bot.sendMessage(chat_ID, text="You are now logged out")
        
        elif self.plant == None  and self.verify:
            self.bot.sendMessage(chat_ID, text="Please select you plant with the following format: \n /plant_id plantnumber")
        elif message.startswith("/irrigation_switch") and self.verify:
            buttons = [[InlineKeyboardButton(text=f'ON', callback_data=f'on'),
                        InlineKeyboardButton(text=f'OFF', callback_data=f'off')]]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            self.bot.sendMessage(chat_ID, text='What do you want to do', reply_markup=keyboard)
            self.plant = message[-1]
        
        elif message.startswith("/health_status") and self.verify:
            health_status =(requests.get(f'http://127.0.0.1:8080/Catalog/Health_Status?user={self.user}&plant={self.plant}').json())
            print(health_status)
            self.bot.sendMessage(chat_ID , text=f"plant number {self.plant} is {health_status['health_status']}  Last Update was on {health_status['Last_Update']}")
        
        elif message.startswith("/irrigation_status"):
            irrigation_status =(requests.get(f'http://127.0.0.1:8080/Catalog/Irrigation_Status?user={self.user}&plant={self.plant}').json())
            self.bot.sendMessage(chat_ID, text=f"plant number {self.plant} has been watered last time at {irrigation_status['time']} , Duration of Irrigation {irrigation_status['duration']}, Number of Irrigations This day {irrigation_status['Number of irrigation This day']}")
        
        else:
            self.bot.sendMessage(chat_ID, text="Command not supported")     
    def on_callback_query(self,msg):
        query_ID , chat_ID , query_data = telepot.glance(msg,flavor='callback_query')
        topic = requests.get(f'http://127.0.0.1:8080/catalog/topics?user={self.user}&plant={self.plant}&program=actuator&type=irrigation').json()
        if query_data == "On":
            self.send_actuation(True,topic)
    
    def send_actuation(self,value:bool,topic: str)-> None :
        self.publish(value,topic)
        
        
        
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    token = (requests.get('http://127.0.0.1:8080/Catalog/ChatBot_token').json())["token"]
    sb=SwitchBot(token)
    while True:
        time.sleep(3)
        

    
               
        
        
        
        
        
        