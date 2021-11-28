from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from binance.client import Client
import binance_helpers as bh

class Downloader: 
    
    PATH = "../data/model/"
    
    def __init__(self):
        """Downloader, with path '../data/model/'"""
        self.client = bh.new_binance_client()
        
    def get_minutely_data(self, pair:str, past=True):
        """smartly downloads and returns minutely data. Enter pair with USDT. If past, returns what is saved,
        else also updates it (without saving) and returns it"""
        
        df_past = self.get_past_bars(pair)

        return df_past if past else self.update_data(pair, df_past)
        

    def update_data(self, pair:str, df_past):
        """smartly updates and returns minutely data. Enter pair with USDT"""        
        df_now = self.binance_download(pair, df_past.iloc[-1].timestamp)
        
        df = df_past[df_past.timestamp < df_now.iloc[0].timestamp]
        df = df.append(df_now, ignore_index=True)
        
        return df
        
    def get_past_bars(self, pair):
        """returns downloaded data if it exists, else downloads and returns"""
        try:
            return self.read_df(pair)
        except:
            df = self.binance_download(pair)
            self.save_df(df, pair)
            return df
        
    def binance_download(self, pair:str, start=1000000000000):
        """
        downloads binance data and returns it. Set save to true to save
        pair: BTCUSDT
        start: float date. Leave as is for from the very beginning (2001). 
        """
        self.client = bh.new_binance_client()
        start_date = self.get_str_date(self.get_date_from_int(start))
        klines = self.client.get_historical_klines(pair, self.client.KLINE_INTERVAL_1MINUTE, start_date, limit=1000)
        data = self.get_filtered_dataframe(klines)
        return data
        
    def get_filtered_dataframe(self, klines):
        """filters columns and converts columns to floats and ints respectively"""
        df = pd.DataFrame(klines, columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore'])
        df = df[['timestamp', 'open']]
        df = df.astype(np.float64)
        df["timestamp"] = df.timestamp.astype(np.int64)
        return df
    
    def get_date_from_int(self, date:int, delay=600):
        """returns datetime object from int minus delay in seconds"""
        return datetime.utcfromtimestamp(date/1000) - timedelta(seconds=delay)
    
    def get_str_date(self, date):
        """returns the string date given datetime date. Use for getting klines"""
        return date.strftime("%d %b %Y %H:%M:%S")
    
    def save_df(self, df, pair):
        """saves the dataframe"""
        df.to_csv(f"{self.PATH + pair}-past.csv", index=False)

    def save_df_fast(self, pair, df, timestamp, buffer=10):
        """update saved df by writing only what it is missing minus buffer minutes"""
        df = df[df.timestamp > timestamp]
        df[:-buffer].to_csv(f"{self.PATH + pair}-past.csv", mode='a', header=False, index=False)

        
    def read_df(self, pair):
        """reads the dataframe"""
        return pd.read_csv(f"{self.PATH + pair}-past.csv")




