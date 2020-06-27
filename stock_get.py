# -*- coding: utf-8 -*-
"""
Created on Sun May 24 01:00:15 2020

@author: runmi
"""
import pandas as pd
import time
from tqdm import tqdm
from pandas_datareader import data 
from pathlib import Path
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
from datetime import date
from statsmodels.api import OLS
import statsmodels.api as sm
#from statsmodels.tsa.vector_ar.vecm import coint_johansen
from IPython.core.debugger import set_trace
from statsmodels.tsa.stattools import adfuller
import matplotlib.pyplot as plt
import ta
import numpy as np
import requests

Path(r'./Company_csv').mkdir(exist_ok=True)
def get(stock='SPY',start=datetime.now() - relativedelta(years=50),end=datetime.now(),snp500=False):
    Path(r'./Company_csv').mkdir(exist_ok=True)
    stock = stock.replace(r'.','-')
    try:
        x = data.get_data_yahoo(stock, start,end)
        try:
            if snp500==False:
                x.to_csv(Path(r'./Company_csv/'+stock+'.csv'))
            else:
                x.to_csv(Path(r'./Company_csv/snp_500',stock+'.csv'))
        except PermissionError as E:
            print(E)
        return x
    except:
        print(f"no data found for: {stock}")
    
    
# returns a dictionary containing all the snp500 holdings
def get_snp500_holdings(start=datetime.now() - relativedelta(years=50),end=datetime.now()):
    all_stock={}
    Path(r'./Company_csv/snp_500').mkdir(exist_ok=True, parents=True)
    
    # the url to download the csv, need to change if become unavail
    url=r'https://datahub.io/core/s-and-p-500-companies/r/constituents.csv'
    r= requests.get(url)
    urlcontent=r.content
    with open('./Company_csv/SPY.csv','wb') as fp:
        fp.write(urlcontent)
        
    data=pd.read_csv(r'./Company_csv/SPY.csv')
    for stock in data['Symbol']:
        
        all_stock[stock]=get(stock,start,end,snp500=True)
            
    
    
    
    return all_stock
    

if __name__=='__main__':
    get_snp500_holdings()
    #print(get('brk.b'))