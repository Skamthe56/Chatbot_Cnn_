#Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

from datetime import datetime
import json
import random
import dateutil.parser
from flask.config import Config
import nltk
import spacy
import re
import torch
#nltk.download('all')
from nltk.tokenize import sent_tokenize, word_tokenize

from model import NeuralNet
from nltk_file import bag_of_words, tokenize
from textblob import TextBlob


from flask import Flask, render_template, redirect, url_for, json
from flask_socketio  import SocketIO
import config
import random
from datetime import datetime

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
#model = NeuralNet(input_size, hidden_size, output_size).to(device)

from dateutil.parser import parse
from scraper import scraper

with open ('intents.json', 'r') as f:
    intents = json.load(f)

#####################################
#Flask code
########################

# Setup socketio
app = Flask(__name__)
app.config.from_object(config.DevelopmentConfig)
socketio = SocketIO(app)

#Render Index
@app.route('/')
@app.route('/chatbot')
def index():
	return render_template('/index.html')

# Display welcome on connect
@socketio.on('connect')
def connect():
	#socketio.emit('display received message',{'message':"Lets chat.! 'quit' to exit", 'time_sent':datetime.now().strftime("%H:%M")})
    send_msg('display received message',"Lets chat.! 'quit' to exit")

# Message handling
@socketio.on('message sent')
def handle_message(json, methods=['GET', 'POST']):
    # Display user message
    send_msg('display sent message',json['message'])

    bot_predict(json['message'])


if __name__ == '__main__':
    socketio.run(app)

#########################################################################################################################

def validateData():
    return True

def getDate(string):
    try:
        date=parse(string)
        date = str(date.day).zfill(2) + str(date.month).zfill(2) + (str(date.year)[2:])
    except:
        send_msg('display received message',"Incorrect date format provided")
        #print("Incorrect date format provided")
    return date

def getTime(string):
    try:
        date=parse(string)
        time = str(date.hour).zfill(2) + str(date.minute).zfill(2)
    except:
        send_msg('display received message',"Incorrect time format provided")
        #print("Incorrect time format provided")
    return time

def is_date(string, fuzzy=False):
    print("inside is date")
    try: 
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False

def send_msg(event_name,message):
    if(event_name != 'display ticket'):
        msg_str={'message':message,'time_sent':datetime.now().strftime("%H:%M")}
    else:
        msg_str=message
    socketio.emit(event_name,msg_str)

FILE="data.pth"
data= torch.load(FILE)
    
input_size= data["input_size"]
hidden_size= data["hidden_size"]
output_size= data["output_size"]
tags= data["tags"]
all_words = data["all_words"]
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()


user_input={}
fromLocat=''
toLocat=''
isReturn=False
return_date=False
ret_time= False
patNo = re.compile(r'\b(?i)(no|nope|nah|false)\b')
patYes = re.compile(r'\b(?i)(yes|yeah|yup|sure|true)\b')

def bot_predict(json_msg):
    global fromLocat, toLocat, user_input, isReturn, return_date, ret_time
    patNo = re.compile(r'\b(?i)(no|nope|nah|false)\b')
    patYes = re.compile(r'\b(?i)(yes|yeah|yup|sure|true)\b')
    sentence= str(json_msg)
    err = False
    #if sentence == "quit":
       # break
    msg=sentence
# tokens1 = nltk.word_tokenize(msg)
    #tagged1 = nltk.pos_tag(tokens1)
    #print("tagged: ",tagged1)

    sentence = tokenize(sentence.lower())
    X=bag_of_words(sentence, all_words)
    X= X.reshape(1,X.shape[0])
    X= torch.from_numpy(X)
    print(sentence)
    output= model(X)

    _,predicted= torch.max(output, dim=1)
    tag= tags[predicted.item()]

    probs= torch.softmax(output, dim=1)
    prob= probs[0][predicted.item()]


    if('from' in sentence):
        ind=sentence.index('from')
        fromLocat = sentence[ind+1]
    if('source' in sentence):
        ind=sentence.index('source')
        fromLocat = sentence[ind+2]
    if('to' in sentence):
        ind=len(sentence)-sentence[::-1].index('to')-1
        toLocat = sentence[ind+1]
    user_input['fromLocat']=fromLocat
    user_input['toLocat']=toLocat

    if(isReturn and patYes.search(msg)):
        if (patYes.search(msg)):
            send_msg('display received message',"Which date would you like to return?")
            return_date=True
            msg=''
            return
    if (return_date and msg !=''):
        #print(f"{bot_name}: Which date would you like to return?")
        #check = True
        retnDate=''
        #while check:
            #err = False
            #msg= input('You:  ')
        
        if(is_date(msg) and not ret_time):
            retnDate=getDate(msg)
            if(dateutil.parser.parse(retnDate) < dateutil.parser.parse(user_input['travelDate'])):
                send_msg('display received message',"Return date has to be greater than travel date. Please enter again")
                return
                #print(f"{bot_name}: Return date has to be greater than travel date. Please enter again")
                
        else:
            send_msg('display received message',"Incorrect date entered. Please enter again")
            return
            #print(f"{bot_name}: Incorrect date entered. Please enter again")

        user_input['returnDate']=retnDate   
        send_msg('display received message',"What time would you like to return?")
        ret_time=True
        return_date=False
        return
        #print(f"{bot_name}: What time would you like to return?")
        #msg= input('You:  ')
        
    
    if(ret_time):
        user_input['returnTime']=getTime(msg)
        ret_time=False
    print("final dict:",user_input)
    if(isReturn):
        isReturn=False
        validateData()
        #scrap= scraper()
        response=scraper.scrape_tickets(user_input)
        #print("response", response)
        send_msg('display ticket', response)
        return


    print("libe 144: ",tag, msg)
    if(is_date(msg)):
        if(tag == 'asktime'):
            user_input['travelDate']=getDate(msg)
            if(dateutil.parser.parse(user_input['travelDate']) < datetime.now()):
                send_msg('display received message',"Travel date cannot be older than today")
                #print(f"{bot_name}: Travel date cannot be older than today")
                tag='askdate'
        if(tag == 'askreturn'):
            user_input['travelTime']=getTime(msg)
    
    
    print("dict:",user_input)
    if prob.item() > 0.75:
    
        for intent in intents["intents"]:
            if tag == intent["tag"]:
                print("tag",tag)
                if(tag == 'askreturn'):
                    isReturn = True
                #user_input[tag]=
                #if tag == 'booking':hellohey
                #hellohey

                    # 
                    #print(f"{bot_name}: {random.choice(intent['responses'])}")
                    #isBooking=False
                send_msg('display received message',random.choice(intent['responses']))
                #print(f"{bot_name}: {random.choice(intent['responses'])}")

    else:
        send_msg('display received message',"I did not understand your response")
        #print(f"{bot_name}: I do not understand...")
