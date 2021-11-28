import binance_helpers as bh
from trader import Trader
from trade import Position, Trade
from strategy import Strategy
import messenger
import schedule
import time
import socket

class Model:
    def __init__(self, strats, min_trade_amt=11, max_slippage=0.2):
        """inits a Model with a list of strategies, minimum trade amount in USDT, and max slippage in %"""
        self.strats = strats #sorted with priority, strats[0] highest priority
        self.min_trade_amt = min_trade_amt
        self.max_slippage = max_slippage
        self.client = bh.new_binance_client()
        
    def update(self):
        """run and forget"""
        trader = Trader() #Need to init a new one because binance client 'expires'
        self.client = bh.new_binance_client()
        try:
            for strat in self.strats:
                p, max_usdt_amt = self.get_position_and_max_trade_value(strat)
                trade = strat.consider_trading(p)
                if trade.to_trade:
                    try:
                        if not trade.liquidate: #buy or sell
                            trade_amt = self.get_trade_amt(trade.long, trade.short, max_usdt_amt)
                            trader.go_long_short(trade.long, trade.short, trade_amt)
                        else: #liquidate
                            max_long = bh.get_order_book(self.client, trade.long, self.max_slippage, False, True)
                            max_short = bh.get_order_book(self.client, trade.short, self.max_slippage, True, True)
                            trader.liquidate(trade.long, trade.short, max_long, max_short, self.min_trade_amt)
                        messenger.update_trade(trade.to_json())
                    except ValueError as e:
                        pass
                messenger.update_strats(strat.a, strat.b, strat.z, strat.thres, strat.sell_thres, strat.max_portfolio)
                strat.save_data()
                messenger.update_time(time.time())
        except socket.timeout:
            print("ERROR: Socket timeout:")
            raise
        except Exception as e:
            print(f"ERROR: {e}")
        return schedule.CancelJob
            
    def turn_on(self):
        schedule.clear()
        schedule.every().minute.at(":01").do(self.update)
        while True:
            try:
                if schedule.get_jobs() != []:
                    schedule.run_pending()
                else:
                    schedule.every().minute.at(":01").do(self.update)
            except socket.timeout:
                rest = 120
                print(f"Socket timeout, sleeping {rest} seconds")
                while True:
                    schedule.clear()
                    time.sleep(rest)
                    try: 
                        schedule.every().minute.at(":01").do(self.update)
                        break
                    except socket.timeout:
                        print(f"Socket timeout again, sleeping an additional 10 seconds, to {rest + 10} seconds")
                        rest += 10
            time.sleep(1)

              
    def get_trade_amt(self, long, short, max_usdt_amt, buffer=0.98):
        """max per-asset trade amount to have slippage within maximum slippage. 
        If below minimum trade amount, throws exception. 
        Buffer is % of USDT balance to use. 98% defaults maximum usage of 98%"""
        mta = max_usdt_amt/2
        usdt_balance = (bh.get_usdt_balance(self.client)/2)*buffer
        max_long = bh.get_order_book(self.client, long, self.max_slippage, True, True)
        max_short = bh.get_order_book(self.client, short, self.max_slippage, False, True)
        trade_amt = min(usdt_balance, max_long, max_short, mta)
        self.assert_above_minimum_trade_amt(trade_amt)
        return trade_amt
    
    def assert_above_minimum_trade_amt(self, trade_amt):
        """throws ValueError if less than minimum trade amount"""
        if trade_amt < self.min_trade_amt:
            raise ValueError(f'Amount to trade ({trade_amt}) below minimum amount ({self.min_trade_amt})')
    
    def get_portfolio_value(self, ima, btc_price):
        """gets the estimated net USDT value of entire portfolio given isolated margin accounts AND
        USDT amount in SPOT account
        REQUIRES: Quote asset in USDT"""
        value = 0
        usdt = bh.get_usdt_balance(self.client)
        value += usdt
        for strat in self.strats:
            value += self.get_pair_value(ima, strat.a, btc_price)
            value += self.get_pair_value(ima, strat.b, btc_price)
        return value, usdt

    def get_pair_value(self, ima, pair:str, btc_price):
        """returns the total USDT value of the strat given pair. REQUIRES pair have USDT as quote. 
        If strat does not exist or has non USDT as quote, returns 0"""
        try:
            strat_val = self.get_pair_from_ima(ima, pair)
            quote_val = float(strat_val['baseAsset']['netAssetOfBtc']) * btc_price
            usdt_val = float(strat_val['quoteAsset']['netAsset'])
            total_val = quote_val + usdt_val
            return total_val
        except:
            return 0.

    def is_short(self, ima, pair:str):
        """returns True if is short this asset (net asset of base is negative). False if asset doesn't exist"""
        try: 
            strat_val = self.get_pair_from_ima(ima, pair)
            quote_val = float(strat_val['baseAsset']['netAssetOfBtc'])
            return quote_val < 0
        except:
            return False

    def get_pair_from_ima(self, ima, pair:str):
        """returns dictionary of pair from isolated margin accounts list of dictionaries. 
        REQUIRES pair has USDT as quote asset"""
        return list(filter(lambda x: x["baseAsset"]["asset"] == pair[:-4], ima["assets"]))[0]

    def get_position_and_max_trade_value(self, strat):
        """gets the current Position of the strat and the maximum value it can buy/short
        until it crosses over strat's maximum allocation"""
        ima = self.client.get_isolated_margin_account()
        btc_price = bh.get_price(self.client, "BTCUSDT")
        pv, usdt = self.get_portfolio_value(ima, btc_price)   #portfolio value
        a_val = self.get_pair_value(ima, strat.a, btc_price)
        b_val = self.get_pair_value(ima, strat.b, btc_price)
        sv = a_val + b_val #Strat value
        mta = (pv * strat.max_portfolio) - sv      #Max trade amount
        
        messenger.update_portfolio_value(pv, usdt, strat.a, strat.b, a_val, b_val)

        position = Position.NONE

        if self.is_short(ima, strat.a):
            if mta > self.min_trade_amt:
                position = Position.B_PARTIAL
            elif mta <= self.min_trade_amt:
                position = Position.B
        elif self.is_short(ima, strat.b):
            if mta > self.min_trade_amt:
                position = Position.A_PARTIAL
            elif mta <= self.min_trade_amt:
                position = Position.A            

        return position, max(0, mta)


