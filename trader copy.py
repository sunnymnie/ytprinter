from strategy import read_strat, save_strat, proofread_strat
from binance.enums import * #https://github.com/sammchardy/python-binance/blob/master/binance/enums.py
import binance_helpers as bh
import time

def trade(strats, interval=1):
    """
    transfers funds to designated margin account, puts in trade, applies stop loss, sells given constraints in strat (5%, 1hr, 3hr). Updates and saves strats when necessary

    pass in strats if can guarantee latest version
    interval is sleep time before checking prices + orders
    """
    print("trader: trade")
    if strats['long'] == None: return
    client = bh.new_binance_client()

    # If did not transfer money from main to new strats['long'] position, do that and then go full on margin and buy. This is the only
    # time where you buy (when you haven't yet transferred the money yet). For all other cases, it is assumed that the asset has already 
    # been bought

    if (strats['pair'][strats['long']]['pos'] == 0): 
        strats['pair'][strats['long']]['pos'] = 1
        save_strat(strats)
        price = transfer_and_buy(client, strats['long'])
        strats = update_strats_with_order(strats, price)

    long_asset = strats['long'] #Do not delete, because setting to null 
    while (strats['long'] != None):

        time.sleep(interval)
        pair = strats['pair'][strats['long']]
        if pair['pos'] != 1: return
        if pair['sl']['pos'] == 1: break

        price = float(client.get_recent_trades(symbol=strats['long'])[-1]['price'])
        now = time.time()

        if (pair['tp']['pos']==0 and price>pair['tp']['pct']): #first time reaching tp
            liquidate(client, strats['long'], pair['tp']['amt'])
            strats['pair'][strats['long']]['tp']['pos'] = 1
            if pair['tp']['amt'] == 1: 
                strats['pair'][strats['long']]['pos'] = -1
                strats['long'] = None
        if (pair['sl']['pos']==0 and price<pair['sl']['pct']): #Hit stop loss, liquidate everything
            # Sell everything
            liquidate(client, strat['long'], 1)
            strats['pair'][strats['long']]['sl']['pos'] = 1
            strats['pair'][strats['long']]['pos'] = -1
            strats['long'] = None
        if (pair['early']['pos']==0 and now>pair['early']['time']):
            # Sell everything for long, then break
            liquidate(client, strats['long'], pair['early']['amt'])
            strats['pair'][strats['long']]['early']['pos'] = 1
            if pair['early']['amt'] == 1: 
                strats['pair'][strats['long']]['pos'] = -1
                strats['long'] = None
        if (pair['late']['pos']==0 and now>pair['late']['time']):
            # Sell everything for long, then break
            liquidate(client, strats['long'], pair['late']['amt'])
            strats['pair'][strats['long']]['late']['pos'] = 1
            strats['pair'][strats['long']]['pos'] = -1
            strats['long'] = None

        save_strat(strats)
    strats = proofread_strat(strats)
    save_strat(strats)
    return strats 


def transfer_and_buy(client, pair):
    """
    transfers all USDT from main to new
    puts in maximum buy order in new for asset
    returns order
    """

    print(f"trader: transfer_and_buy {pair}")
    symbol = pair[:-4]
    usdt_spot_free = client.get_asset_balance(asset='USDT')['free']
    client.transfer_spot_to_isolated_margin(asset='USDT', symbol=pair, amount=usdt_spot_free)

    # Take out loan for max
    max_loan = client.get_max_margin_loan(asset='USDT', isolatedSymbol=pair)['amount']
    client.create_margin_loan(asset='USDT', amount=max_loan, symbol=pair, isIsolated='TRUE')

    # Find out how much asset to buy
    dp = bh.get_decimal_place(client, pair)
    price = float(client.get_recent_trades(symbol=pair)[-1]['price'])
    m = client.get_isolated_margin_account()
    usdta = list(filter(lambda x: x['baseAsset']['asset'] == symbol and x['quoteAsset']['asset'] == 'USDT', m['assets']))[0]
    usdta = float(usdta['quoteAsset']['free'])
    amt = bh.binance_floor(0.95*usdta/price, dp)

    # Buy asset
    order = client.create_margin_order(
        symbol=pair,
        side=SIDE_BUY,
        type=ORDER_TYPE_MARKET,
        quantity=amt,
        newOrderRespType = "RESULT",
        isIsolated='TRUE')

    return float(client.get_recent_trades(symbol=pair)[-1]['price'])


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

def liquidate(client, pair, pct):
    """
    liquidates pct (0, 1.0] of the entire portfolio given pair. Does not transfer back to spot unless 1.0 is liquidated
    """

    print(f"trader: liquidate {pct*100}% of {pair} position")
    symbol = pair[:-4]
    dp = bh.get_decimal_place(client, pair)
    m = client.get_isolated_margin_account()
    samt = list(filter(lambda x: x['baseAsset']['asset'] == symbol and x['quoteAsset']['asset'] == 'USDT', m['assets']))[0]
    samt = bh.binance_floor(float(samt['baseAsset']['free'])*pct, dp)

    order = client.create_margin_order(
        symbol=pair,
        side=SIDE_SELL,
        type=ORDER_TYPE_MARKET,
        quantity=samt,
        newOrderRespType = "RESULT",
        isIsolated='TRUE')

    m = client.get_isolated_margin_account()
    m = list(filter(lambda x: x['baseAsset']['asset'] == symbol and x['quoteAsset']['asset'] == 'USDT', m['assets']))[0]
    f = m['quoteAsset']['free']
    b = float(m['quoteAsset']['borrowed'])
    if b!=0:  client.repay_margin_loan(asset='USDT', amount=f, symbol=pair, isIsolated='TRUE')

    if pct==1: 
        print("trader: transfer funds back to spot")
        m = client.get_isolated_margin_account()
        m = list(filter(lambda x: x['baseAsset']['asset'] == symbol and x['quoteAsset']['asset'] == 'USDT', m['assets']))[0]
        tamt = m['quoteAsset']['free']
        bamt = m['baseAsset']['free']
        client.transfer_isolated_margin_to_spot(asset='USDT', symbol=pair, amount=tamt)
        client.transfer_isolated_margin_to_spot(asset=symbol, symbol=pair, amount=bamt)

