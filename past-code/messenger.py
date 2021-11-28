import json
import pandas as pd
from datetime import datetime

MESSAGE = 'message.txt'
HISTORY = 'history.txt'

def get_message():
    """gets message"""
    return open_json(MESSAGE)

def save_message(message):
    """saves message"""
    save_json(message, MESSAGE)

def open_json(filename):
    """opens json file"""
    with open(filename) as json_file:
        return json.load(json_file)
    
def save_json(file, filename):
    """saves json file"""
    with open(filename, 'w') as outfile:
        json.dump(file, outfile)
        
def update_time(time):
    """saves the time to last_update on file"""
    message = open_json(MESSAGE)
    message["last_update"] = datetime.fromtimestamp(time).strftime("%d %B, %H:%M:%S")
    save_json(message, MESSAGE)
    
def update_trade(trade):
    """saves trade to message.txt for discord manager to post"""
    message = open_json(MESSAGE)
    message["trades"].append(trade)
    save_json(message, MESSAGE)
    
def update_strats(a, b, z, thres, sell_thres, max_portfolio):
    """saves strat info"""
    strat = get_strat_name(a, b)
    message = open_json(MESSAGE)
    message = optionally_init_strat(message, strat)
    message["strategy"][strat]["z"] = z
    message["strategy"][strat]["thres"] = thres
    message["strategy"][strat]["sell_thres"] = sell_thres
    message["strategy"][strat]["max_portfolio"] = max_portfolio
    save_json(message, MESSAGE)
    
def update_portfolio_value(pv, usdt, a, b, a_val, b_val):
    """updates portfolio value and saves it"""
    strat = get_strat_name(a, b)
    message = open_json(MESSAGE)
    message["portfolio"] = {'usdt': usdt, 'total': pv}
    message = optionally_init_strat(message, strat)
    message["strategy"][strat]["pct"] = (a_val + b_val)/pv
    message["strategy"][strat]["a"] = a_val
    message["strategy"][strat]["b"] = b_val
    save_json(message, MESSAGE)
    
def optionally_init_strat(message, strat):
    """returns message if strat exists, else inits strat and returns message"""
    try:
        message["strategy"][strat]
    except:
        message["strategy"][strat] = {}
    return message
    
def get_strat_name(a, b):
    """returns strat name removing USDT"""
    a = a[:-4]
    b = b[:-4]
    return a + b
    
def keep_track_of_order(order):
    """saves order or transaction to json"""
    message = open_json(MESSAGE)
    history = open_json(HISTORY)
    history["order"].append(order)
    history["portfolio"].append(message["portfolio"])
    save_json(history, HISTORY)
