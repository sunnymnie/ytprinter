#import binance client
from downloader import Downloader
from magic import Magic
from trade import Position, Trade

class Strategy:
    def __init__(self, a, b, thres, sell_thres, lookback, max_portfolio):
        self.a = a                          # FETUSDT
        self.b = b                          # CELRUSDT
        self.thres = thres                  # 3.4
        self.sell_thres = sell_thres        # 0.25
        self.max_portfolio = max_portfolio  # 0.8
        self.m = Magic(lookback)
        self.long = Position
        self.dl = Downloader()
        
        self.df_a = self.dl.get_minutely_data(self.a)
        self.df_b = self.dl.get_minutely_data(self.b)
        self.time_of_last_save_a = self.df_a.iloc[-1].timestamp
        self.time_of_last_save_b = self.df_b.iloc[-1].timestamp
        self.z = self.m.get_z_score(self.df_a, self.df_b)
        
    def update_data(self):
        """updates df_a, and df_b"""
        self.df_a = self.dl.update_data(self.a, self.df_a)
        self.df_b = self.dl.update_data(self.b, self.df_b)
        
    def consider_trading(self, p):
        """If trading opportunity, returns trade object, does not tell how much to trade"""
        self.update_data()
        self.z = self.m.get_z_score(self.df_a, self.df_b)
        trade = Trade(False)
        
        trade = self.consider_liquidating(p)
        trade = self.consider_long_short(p) if not trade.to_trade else trade

        return trade
        
            
    def consider_long_short(self, p):
        """consider a long trade or a short trade"""
        if (self.z > self.thres) and (p == self.long.A_PARTIAL or p == self.long.NONE):
            return Trade(True, False, self.a, self.b)
        elif (self.z < -self.thres) and (p == self.long.B_PARTIAL or p == self.long.NONE):
            return Trade(True, False, self.b, self.a)
        return Trade(False)
    
    def consider_liquidating(self, p):
        if (self.z < -self.sell_thres) and (p == self.long.A or p == self.long.A_PARTIAL):
            return Trade(True, True, self.a, self.b)
        elif (self.z > self.sell_thres) and (p == self.long.B or p == self.long.B_PARTIAL):
            return Trade(True, True, self.b, self.a)
        return Trade(False)
        
        
    def save_data(self):
        """saves dfs and sets time of last save"""
        self.time_of_last_save_a = self.dl.save_df_fast(self.a, self.df_a, self.time_of_last_save_a)
        self.time_of_last_save_b = self.dl.save_df_fast(self.b, self.df_b, self.time_of_last_save_b)
