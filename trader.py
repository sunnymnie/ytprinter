import pandas as pd
import numpy as np
from strategy import read_strat, save_strat

def trade(strats, interval=10):
    """
    transfers funds to designated margin account, puts in trade, applies stop loss, sells given constraints in strat (5%, 1hr, 3hr). Updates and saves strats when necessary

    pass in strats if can guarantee latest version
    interval is sleep time before checking prices + orders
    """

    if strats['long'] = None: return

    # If did not transfer money from main to new strats['long'] position, do that and then go full on margin and buy. This is the only
    # time where you buy (when you haven't yet transferred the money yet). For all other cases, it is assumed that the asset has already 
    # been bought

    if (strats['pair'][strats['long']]['pos'] == 0): 
        strats['pair'][strats['long']]['pos'] = 1
        save_strat(strats)
        order = transfer_and_buy(strats['main'], strats['long'])
        strats = update_strats_with_order(strats, order)

    while (strats['long'] != None):
        pair = strats['pair'][strats['long']]
        if pair['pos'] != 1: return
        if pair['sl']['pos'] == 1: break

        price = ...Get latest binance price for asset
        now = ...Get latest time

        if (pair['tp']['pos']==0 and price>pair['price']*(1+pair['tp']['pct'])): #first time reaching tp
            # Sell amt
        if (pair['sl']['pos']==0 and price<pair['price']*(1-pair['sl']['pct'])): #Hit stop loss, liquidate everything
            # Sell everything
            # break
        if (...time for two options...):
            # Sell everything for long, then break
            pass
    strats['pair'][strats['long']]['pos'] = -1


        


    # If there is very little


def transfer_and_buy(main, new):
    """
    transfers all USDT from main to new
    puts in maximum buy order in new for asset
    returns order
    """


    return order

def update_strats_with_order(strats, order):
    """
    updates strats with order info and saves new strats and returns it
    - updates buy price
    """
    strats['pair'][strats['long']]['price'] = ...order...buy price
    save_strat(strats)
    return strats

