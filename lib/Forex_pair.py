#!/usr/bin/env python
# coding: utf-8

# In[1]:


#get_ipython().system(' pip install oandapyV20')


# In[4]:


#get_ipython().system('pip install regex')


# In[2]:


#import v20
import json
from oandapyV20 import API
from oandapyV20 import V20Error
import oandapyV20.endpoints.trades as trades
import oandapyV20.endpoints as EP
import oandapyV20.endpoints.pricing as pricing
import oandapyV20.endpoints.instruments as instruments
import pandas as pd
import numpy  as np

import ta
import datetime
from dateutil.relativedelta import relativedelta
from datetime import date
from statsmodels.tsa.stattools import adfuller
import time
import regex as re
from IPython.core.debugger import set_trace


# In[3]:
'''
# set ago to the period to lookback from today in terms of month
class import_dataset(self,price='mid',start=datetime.datetime.today() - relativedelta(months=3),end=datetime.datetime.today(),test_train_ratio=1/3,K_fold=3)

df=import_dataset()


# ## check dataset
# #### all data store in df.Dict_pairs_df




'''


class import_dataset:
    def __init__(self,price='mid',start=datetime.datetime.today() - relativedelta(months=3),end=datetime.datetime.today(),test_train_ratio=1/3,K_fold=3,ago=None):
  
        self.Dict_pairs_df={}
        self.Pairs_list=[]
        if ago!=None:
            self.start = date.strftime(datetime.datetime.today() - relativedelta(months=ago),'%Y-%m-%d')
            print('data for past %s month'%(ago))
        elif start!=None:
            
            if type(start)==str:
                self.start=start
                print('1')
            else:
                self.start=date.strftime(start,'%Y-%m-%d')
                print('2 - ',self.start )
  
        if type(end)==str:
            self.end=end
        else:
            self.end=date.strftime(end,'%Y-%m-%d')
        self.price=price
        if price=='mid':
            self.Price='M'
        elif price=='ask':
            self.Price='A'
        elif price=='bid':
            self.Price=='B'
        else:
            self.price='mid'
            self.Price='M'
            
        self.list_majors=['EUR','GBP','AUD','JPY','USD','NZD','CAD']
        
        self.acct_info=pd.read_csv('OandaAPI_keys.csv',header=None)
        self.api = API(access_token=self.acct_info.iloc[0,1],environment='practice')
        self.accountID = self.acct_info.iloc[1,1]
        
        self.import_Dataset()
                                
    def import_Dataset(self):
       for Front in self.list_majors:
           for Back in self.list_majors:
                if Front!=Back:
                    instrument=Front+'_'+Back
                    params = {

                            #"count": 2
                            "granularity": "D"
                           ,'dailyAlignment':0
                           ,'price':self.Price
                           
                            }

                    x=instruments.InstrumentsCandles(instrument=instrument, params=params)
                    try:
                        t=self.api.request(x)
                        
                        # pulling out each dataset from the dictionary pulled from Oanda
                        print('\nRequest successful: ',instrument)
                        Price=[x[self.price] for x in t['candles']]
                        time={'Date':[x['time'] for x in t['candles']]}
                        Vol={'Vol':[x['volume'] for x in t['candles']]}
                        
                        # putting the file into DataFrame to concat later
                        price_df=pd.DataFrame(Price,dtype='float')
                        time_df=pd.DataFrame(time)
                        vol_df=pd.DataFrame(Vol,dtype='float')
                        
                        # reorganise the df
                        # slice the Date col so only the date remain and the time is remove
                        time_df['Date']=time_df['Date'].str.slice(0,10)
                        f=pd.concat([time_df,price_df,vol_df],axis=1)
                        f.set_index('Date',inplace=True)
                        f=f.loc[:,['o','h','l','c','Vol']]
                        self.All_Data=f
                       
         
                        # add to a dictionary of major cross pairs
                        print('Start Date: ',self.start)
                        self.Dict_pairs_df[instrument]=f.loc[self.start:,:]
                    except V20Error:
                        #print('\nPairs not found: %s'%instrument)
                        continue
  
            
                
            
        
if __name__=="__main__":
    df=import_dataset(start='2017-12-20')
    print(df.Dict_pairs_df['EUR_GBP'])


# In[4]:






