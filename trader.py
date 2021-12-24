from strategy import read_strat, save_strat, proofread_strat
from binance.enums import * #https://github.com/sammchardy/python-binance/blob/master/binance/enums.py
import binance_helpers as bh
import time
import threading

def get_futures_price(client, pair):
    """returns futures price for pair"""
    return float(client.futures_symbol_ticker(symbol=pair)['price'])

def get_futures_holdings(client, pair):
    """
    returns amount of 'pair' held in futures cross margin account
    """
    return float(list(filter(lambda x: x['symbol'] == pair.upper(), client.futures_position_information()))[0]['positionAmt'])

def futures_long_trade(client, pair, leverage, usdt):
    """
    Creates a future long trade for pair with leverage for 95%*leverage*usdt amount
    returns average price bought at
    """
    dp = bh.get_futures_precision(client, pair)
    amt = 0.95*leverage*usdt/get_futures_price(client, pair)
    amt = bh.binance_floor(float(amt), dp)
    order = _futures_trade(client, pair, amt, "BUY")
    price = client.futures_get_order(symbol=pair, orderId=order['orderId'])['avgPrice']
    return float(price)

def futures_short_trade(client, pair, amt):
    """Creates a future short trade for pair with leverage for amt"""
    dp = bh.get_futures_precision(client, pair)
    amt = bh.binance_floor(float(amt), dp)
    order = _futures_trade(client, pair, amt, "SELL")
    price = client.futures_get_order(symbol=pair, orderId=order['orderId'])['avgPrice']
    return float(price)
    

def _futures_trade(client, pair, amt, side):
    """private helper to create futures trade"""

    return client.futures_create_order(
        symbol=pair,
        type='MARKET',
        side=side,
        quantity=amt
    )

def transfer_futures_to_cross_margin(client, amt=None):
    """
    transfers USDT in futures account to margin account
    - amt: float. If none, withdraws all USDT to cross margin
    """
    if amt is None: amt = float(list(filter(lambda x: x['asset'] == 'USDT', client.futures_account_balance()))[0]['withdrawAvailable'])
    client.futures_account_transfer(asset="USDT", amount=amt, type=2)
    client.transfer_spot_to_margin(asset='USDT', amount=str(amt))

def transfer_cross_margin_to_futures(client, amt):
    """
    transfers USDT in cross margin account to given futures account
    - amt: float
    """
    client.transfer_margin_to_spot(asset='USDT', amount=str(amt))
    client.futures_account_transfer(asset="USDT", amount=amt, type=1)

def liquidate_cross_margin_account(client, pairs):
    """
    liquidates everything in cross margin account to USDT
    If cannot liquidate a particular pair, prints out warning and moves on
    """
    threads = []
    for pair in pairs:
        t = threading.Thread(target=margin_order, args=(client, f"{pair['asset']}USDT", 'SELL', float(pair['free'])))
        threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join()

def cross_margin_long_trade(client, pair, amt):
    """goes long pair with amt in cross margin"""
    _margin_order(client, pair, 'BUY', amt)

def get_cross_margin_snapshot(client):
    """gets a snapshot of the cross margin account and returns it"""
    portfolio = client.get_margin_account()
    portfolio = list(filter(lambda x: x['free'] != '0', portfolio['userAssets']))
    return [dict([a, _try_float(x)] for a, x in b.items()) for b in portfolio]


def _try_float(x):
    """tries to convert to float"""
    try: return float(x)
    except: return x



def update_strats_with_order(strats, price):
    """
    updates strats with order info and saves new strats and returns it
    - updates buy price
    """
    now = time.time()
    strats['pair'][strats['long']]['tp']['pct'] *= price
    strats['pair'][strats['long']]['sl']['pct'] *= price
    strats['pair'][strats['long']]['early']['time'] += now
    strats['pair'][strats['long']]['late']['time'] += now

    save_strat(strats)
    return strats

def margin_order(client, pair, side, amt, isolated='FALSE'):
    """Safe margin order. Will print warning if failed"""
    try:
        return _margin_order(client, pair, side, amt, isolated)
    except:
        print(f"Warning: failed to liquidate {amt} {pair}USDT")


def _margin_order(client, pair, side, amt, isolated='FALSE'):
    """
    puts in and returns margin market order. Auto does decimal-point calculation to amt
    - pair: str (ie "BTCUSDT")
    - side: 'BUY', 'SELL'
    - amt: float
    - isolated: default 'FALSE', 'TRUE' for isolated margin. 
    """
    dp = bh.get_decimal_place(client, pair)
    amt = bh.binance_floor(float(amt), dp)
    order = client.create_margin_order(
        symbol=pair,
        side=side,
        type=ORDER_TYPE_MARKET,
        quantity=amt,
        newOrderRespType = "RESULT",
        isIsolated=isolated)
    return order

