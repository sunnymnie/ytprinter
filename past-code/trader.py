import binance_helpers as bh
from binance.enums import * #https://github.com/sammchardy/python-binance/blob/master/binance/enums.py
import messenger

class Trader:
    
    def __init__(self):
        """inits a new trader that can fulfill trade obligations given by Model"""
        self.client = bh.new_binance_client()
        
    def go_long_short(self, long, short, usdt_amt):
        """places a market order to go long and takes a loan to go short"""
        
        l_asset = long[:-4]
        s_asset = short[:-4]
        
        usdt_amt = bh.binance_floor(0.99*usdt_amt, 6)
        
        self.client.transfer_spot_to_isolated_margin(asset='USDT', symbol=long, amount=str(usdt_amt))
        self.client.transfer_spot_to_isolated_margin(asset='USDT', symbol=short, amount=str(usdt_amt))
        
        l_dp = bh.get_decimal_place(self.client, long)
        s_dp = bh.get_decimal_place(self.client, short)
        
        l_asset_price = bh.get_price(self.client, long)
        s_asset_price = bh.get_price(self.client, short)
        
        l_amt = bh.binance_floor(usdt_amt*0.97/l_asset_price, l_dp)
        s_amt = bh.binance_floor(usdt_amt*0.97/s_asset_price, s_dp) 
        
        self.go_short(short, s_asset, s_amt)
        self.go_long(long, l_asset, l_amt)
        
    def go_long(self, long, l_asset, amt):
        """goes long amt amount of long"""
        order = self.client.create_margin_order(
            symbol=long,
            side=SIDE_BUY,
            type=ORDER_TYPE_MARKET,
            quantity=amt,
            newOrderRespType = "FULL",
            isIsolated='TRUE')
        messenger.keep_track_of_order(order)
    
    def go_short(self, short, s_asset, amt):
        """goes short amt amount of short"""
        transaction = self.client.create_margin_loan(asset=s_asset, amount=str(amt), isIsolated='TRUE', symbol=short)
        order = self.client.create_margin_order(
            symbol=short,
            side=SIDE_SELL,
            type=ORDER_TYPE_MARKET,
            quantity=amt,
            newOrderRespType = "FULL",
            isIsolated='TRUE')
        messenger.keep_track_of_order(transaction)
        messenger.keep_track_of_order(order)
    
        
    def liquidate(self, long, short, max_long, max_short, min_trade_amt):
        """liquidates current long and short position but under max_usdt_amt. If remaining 
        short position or long position is less than min_trade_amt, liquidate function ignores max_usdt_amt
        and liquidates all"""
        l_asset = long[:-4]
        s_asset = short[:-4]
        
        l_asset_price = bh.get_price(self.client, long)
        s_asset_price = bh.get_price(self.client, short)
        
        l_dp = bh.get_decimal_place(self.client, long)
        s_dp = bh.get_decimal_place(self.client, short)
        
        l_amt_base = bh.binance_floor(float(bh.get_margin_asset(self.client, l_asset)["free"]), l_dp)
        s_amt_base = bh.binance_ceil(abs(float(bh.get_margin_asset(self.client, s_asset)["netAsset"])), s_dp) #Positive
        
        l_usdt_amt = l_amt_base * l_asset_price
        s_usdt_amt = s_amt_base * s_asset_price
        
        l_pct = min(max_long/l_usdt_amt, 1)  # % of long position you can sell
        s_pct = min(max_short/s_usdt_amt, 1) # % of short position you can sell
        max_pct = min(l_pct, s_pct)          # max % to sell for both assets
        r_pct = 1-max_pct                   # % of portfolio left if sold max_pct for both
        
        
        l_amt = max_pct*l_usdt_amt #long position to sell 
        l_r_amt = r_pct*l_usdt_amt #long position remaining
        s_amt = max_pct*s_usdt_amt #long position to sell
        s_r_amt = r_pct*s_usdt_amt #long position remaining
        
        
        
        sell_all = False
        
        if (l_amt > min_trade_amt) and (l_r_amt > min_trade_amt):
            #sell that much long position
            l_amt_to_sell = bh.binance_floor(max_pct*l_amt_base, l_dp)
            self.liquidate_long_position(long, l_amt_to_sell)
        elif (l_r_amt > min_trade_amt): # $100 left but current max of buying $5, sell $20
            self.liquidate_long_position(long, bh.binance_floor(min_trade_amt/l_asset_price, l_dp))
        else: #only $30 left, sell $10, or sell $25
            #attempt to sell all
            sell_all = True
            
        if (s_amt > min_trade_amt) and (s_r_amt > min_trade_amt):
            #sell that much long position
            s_amt_to_buy = bh.binance_ceil(max_pct*s_amt_base, s_dp)
            self.liquidate_short_position(short, s_asset, s_amt_to_buy)
        elif (s_r_amt > min_trade_amt): # $100 left but current max of buying $5, sell $20
            self.liquidate_short_position(short, s_asset, bh.binance_floor(min_trade_amt/s_asset_price, s_dp))
        elif sell_all: #only $30 left, sell $10, or sell $25
            #attempt to sell all
            # Assumes there's enough to sell (ie not $5 left)
            self.liquidate_long_position(long, l_amt_base)
            self.liquidate_short_position(short, s_asset, s_amt_base)
            
        self.repay_loan(short, s_asset)
        self.move_money_to_spot(long, short, l_asset, s_asset)

        
    def liquidate_long_position(self, pair, amt):
        """liquidate the long position"""
        order = self.client.create_margin_order(
            symbol=pair,
            side=SIDE_SELL,
            type=ORDER_TYPE_MARKET,
            quantity=amt,
            newOrderRespType = "FULL",
            isIsolated='TRUE')
        messenger.keep_track_of_order(order)
            
    def liquidate_short_position(self, pair, asset, amt):
        """liquidates short position and repays loan"""
        order = self.client.create_margin_order(
            symbol=pair,
            side=SIDE_BUY,
            type=ORDER_TYPE_MARKET,
            quantity=amt,
            newOrderRespType = "FULL",
            isIsolated='TRUE')
        messenger.keep_track_of_order(order)
        
    def repay_loan(self, short, s_asset):
        """repays loan"""        
        rp = str(abs(float(bh.get_margin_asset(self.client, s_asset)["free"])))
        
        if float(rp)>0:
            transaction = self.client.repay_margin_loan(asset=s_asset, amount=rp, isIsolated='TRUE', symbol=short)
            messenger.keep_track_of_order(transaction)
            
    def move_money_to_spot(self, long, short, l_asset, s_asset):
        """moves all money to spot. Assumes finished closing out of trade"""
        l_usdt = str(bh.binance_floor(float(bh.get_isolated_margin_account(self.client, l_asset)["quoteAsset"]["free"]), 6))
        s_usdt = str(bh.binance_floor(float(bh.get_isolated_margin_account(self.client, s_asset)["quoteAsset"]["free"]), 6))

        if float(l_usdt) > 0.1:
            self.client.transfer_isolated_margin_to_spot(asset='USDT', symbol=long, amount=l_usdt)
        if float(s_usdt) > 0.1:
            self.client.transfer_isolated_margin_to_spot(asset='USDT', symbol=short, amount=s_usdt)
        
    def update_client(self):
        self.client = bh.new_binance_client()
        