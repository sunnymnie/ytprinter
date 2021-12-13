from strategy import read_strat, save_strat, proofread_strat
from binance.enums import * #https://github.com/sammchardy/python-binance/blob/master/binance/enums.py
import time
import trader as t
import datetime
import binance_helpers as bh

def manage_position(strats, interval = 1):
    """
    transfers funds to futures account, puts in trade, applies stop loss, sells given constraints in strat (5%, 1hr, 3hr). Updates and saves strats when necessary

    pass in strats if can guarantee latest version
    interval is sleep time before checking prices + orders
    """
    print(f"Portfolio manager activated at {datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-8))).strftime('%H:%M:%S')}")
    if strats['long'] == None: return
    client = bh.new_binance_client()

    if (strats['pair'][strats['long']]['pos'] == 0):
        client.futures_change_leverage(symbol=strats['long'], leverage=strats['pair'][strats['long']]['leverage'])

        # TODO Take snapshot of current holdings, save 
        portfolio = t.get_cross_margin_snapshot(client)
        # TODO Liquidate current holdings
        pairs = list(filter(lambda x: x['asset'] != 'USDT', portfolio))
        t.liquidate_cross_margin_account(client, pairs)

        # TODO Transfer USDT to futures account
        usdt = float(client.get_max_margin_transfer(asset='USDT')['amount']) #float
        t.transfer_cross_margin_to_futures(client, usdt)

        # TODO Buy on futures acount
        price = t.futures_long_trade(client, strats['long'], strats['pair'][strats['long']]['leverage'], usdt)
        print(f"Going long {strats['long']} at {datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-8))).strftime('%H:%M:%S')} with price {str(price)}")
        strats = update_strats_with_price(strats, price)
        strats['pair'][strats['long']]['pos'] = 1
        strats['portfolio'] = portfolio
        save_strat(strats)
    
    amount = t.get_futures_holdings(client, strats['long'])

    while (strats['long'] != None):
        time.sleep(interval)
        pair = strats['pair'][strats['long']]
        if pair['pos'] != 1: return
        if pair['sl']['pos'] == 1: break

        price = t.get_futures_price(client, strats['long'])
        now = time.time()

        if (pair['tp']['pos']==0 and price>pair['tp']['pct']): #first time reaching tp
            print(f"Take profit activated at {datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-8))).strftime('%H:%M:%S')}")
            t.futures_short_trade(client, strats['long'], pair['tp']['amt']*amount)
            strats['pair'][strats['long']]['tp']['pos'] = 1
            if pair['tp']['amt'] == 1:
                t.transfer_futures_to_cross_margin(client)
                strats = full_liquidate_strat(strats)
        if (pair['sl']['pos']==0 and price<pair['sl']['pct']): #Hit stop loss, liquidate everything
            # Sell everything
            print(f"Stop loss activated at {datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-8))).strftime('%H:%M:%S')}")
            t.futures_short_trade(client, strats['long'], amount)
            strats['pair'][strats['long']]['sl']['pos'] = 1
            t.transfer_futures_to_cross_margin(client)
            strats = full_liquidate_strat(strats)

        if (pair['early']['pos']==0 and now>pair['early']['time']):
            # Sell everything for long, then break
            print(f"Early time-stop activated at {datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-8))).strftime('%H:%M:%S')}")
            t.futures_short_trade(client, strats['long'], pair['early']['amt']*amount)
            strats['pair'][strats['long']]['early']['pos'] = 1
            if pair['early']['amt'] == 1: 
                t.transfer_futures_to_cross_margin(client)
                strats = full_liquidate_strat(strats)
        if (pair['late']['pos']==0 and now>pair['late']['time']):
            # Sell everything for long, then break
            print(f"Late time stop activated at {datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-8))).strftime('%H:%M:%S')}")
            t.futures_short_trade(client, strats['long'], pair['late']['amt']*amount)
            strats['pair'][strats['long']]['late']['pos'] = 1
            t.transfer_futures_to_cross_margin(client)
            strats = full_liquidate_strat(strats)

        save_strat(strats)
    strats = proofread_strat(strats)
    save_strat(strats)
    return strats

def init_previous_portfolio(strats):
    """
    inits previous portfolio with 'leverage' amount of assets
    """
    client = bh.new_binance_client()
    total = 0
    for pair in strats['portfolio']:
        if pair['asset'] == 'USDT': continue
        amt = pair['free']
        price = bh.get_price(client, f"{pair['asset']}USDT")
        total += amt*price

    usdt = list(filter(lambda x: x['asset'] == 'USDT', t.get_cross_margin_snapshot(client)))[0]['free']
    usdt *= strats['leverage']

    for pair in strats['portfolio']:
        if pair['asset'] == 'USDT': continue
        pct = pair['free']/total
        amt = pct*usdt
        try: t.cross_margin_long_trade(client, f"{pair['asset']}USDT", amt)
        except: print(f"Warning: unable to buy {amt} {pair['asset']}USDT")
    print(f"Successfully init previous portfolio at {datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-8))).strftime('%H:%M:%S')}")



def full_liquidate_strat(strats):
    """
    inputs data for fully liquidated strats and returns it
    """
    strats['pair'][strats['long']]['pos'] = -1
    strats['long'] = None
    return strats


def update_strats_with_price(strats, price):
    """
    updates strats with price info and returns it
    - updates buy price
    """
    now = time.time()
    strats['pair'][strats['long']]['tp']['pct'] *= price
    strats['pair'][strats['long']]['sl']['pct'] *= price
    strats['pair'][strats['long']]['early']['time'] += now
    strats['pair'][strats['long']]['late']['time'] += now

    return strats


