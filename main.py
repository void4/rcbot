import json
import logging
import requests
from time import sleep
from random import randint, choice

from actioncable.connection import Connection
from actioncable.subscription import Subscription

from settings import *

# ==== REST API ================================================================

def post(j, id=None):
    if id is None:
        id = BOTID
    return requests.post(BOTURL+id, json=j, auth=(app_id, app_secret))

def patch(j, id=None):
    if id is None:
        id = BOTID
    return requests.patch(BOTURL+id, json=j, auth=(app_id, app_secret))

def delete(j=None, id=None):
    if id == None:
        id = BOTID
    if j is None:
        return requests.delete(BOTURL+id, auth=(app_id, app_secret))
    else:
        return requests.delete(BOTURL+id, json=j, auth=(app_id, app_secret))


# ==== ACTIONCABLE =============================================================

#logging.basicConfig(level=logging.DEBUG)

connection = Connection(url=f"wss://recurse.rctogether.com/cable?app_id={app_id}&app_secret={app_secret}", origin='https://recurse.rctogether.com')
connection.connect()

subscription = Subscription(connection, identifier={'channel': 'ApiChannel'})

# WORLD STATE
BOTID = None
steps = 0

STARTX = 16
STARTY = 16

world = None

def on_receive(message):
    global steps, STARTX, STARTY
    #print('New message arrived!')
    #print('Data: {}'.format(message))
    if message["type"] == "world":
        world = message["payload"]
        print("world received")
        for entity in world["entities"]:
            #if entity.get("name") == "codabot":
            #print(entity)
            if entity["type"] == "Bot":
                if entity.get("name") == BOTNAME:
                    delete(id=str(entity["id"]))
            elif entity.get("person_name") == BOTFOLLOW:
                STARTX = entity["pos"]["x"]
                STARTY = entity["pos"]["y"]

        init()
    elif message["type"] == "entity":
        #print(message)
        message = message["payload"]
        if message.get("person_name") == BOTFOLLOW:
            if BOTID:
                def rdist(mi=1,ma=3):
                    return randint(mi, ma)*choice([-1,1])
                data =  {"x":message["pos"]["x"]+rdist(), "y":message["pos"]["y"]+rdist()}
                if steps % 4 == 0:
                    patch(data)
                steps += 1
    else:
        print("Unknown message type", message["type"])

subscription.on_receive(callback=on_receive)
subscription.create()

def init():
    global BOTID
    req = post({"bot":{"name":BOTNAME, "x":STARTX, "y":STARTY, "emoji":BOTEMOJI}}, id="")
    bot = req.json()
    BOTID = str(bot["id"])

try:
    while True:
        print(subscription.state)
        sleep(1)
        pass
except KeyboardInterrupt:
    if BOTID:
        delete()
