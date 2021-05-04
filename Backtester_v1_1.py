# -*- coding: utf-8 -*-
"""
Created on Tue Feb  9 16:03:02 2021
upcoming updates
- gap down stop out
- close out without reversing position
- no trade timing
    - 15min before end of session

@author: Admin
"""

import numpy as np
import pandas as pd
import importlib
import math
import sys
import time

from datetime import datetime

import Summary as S
importlib.reload(S)
def Avg_price(Entryprice,position):
    '''
    return an integer of a weighted average price of all positions
    and the total number of position
    
    Entryprice and position must be a row vector with the same size
    Total position=np.sum(position)
    avg_price=np.dot(position,Entryprice.T)/Total_position
    '''
    
    Entryprice=np.array(Entryprice)
    #print('\nEntry: ',Entryprice)
    position=np.array(position)
    #print('position: ',position)
    Total_position=np.sum(position)
    avg_price=np.dot(position,Entryprice.T)/Total_position
    #print('avg Price: ',avg_price,'TOtal P: ',Total_position)
    return avg_price,Total_position

def initialise_setting():
    ''' reset to the following settings
    EntryPrice=[]
    avg_EntryPrice=None
    ExitPrice={'Stop':np.array([]),"TP":np.array([])}
    position=[]
    Total_Position=0
    '''
    EntryPrice=np.nan

    ExitPrice={'Stop':np.nan,"TP":np.nan}
    Position=0
    
    return EntryPrice,ExitPrice,Position


class Backtester:
    def __init__(self,df,Stop=10,Troubleshoot=False,tick_size=0.5,TP=15,Slippage=1,CAGR_N=1,Return_df=True,Uni_Direction=np.nan):
        self.temp_df=df.copy()
        
        self.Stop=Stop
        self.Troubleshoot=Troubleshoot
        self.tick_size=tick_size
        self.TP=TP
        self.Slippage=Slippage
        self.CAGR_N=CAGR_N
        self.Return_df=Return_df
        self.Uni_Direction=Uni_Direction
        self.PL_list=[]
        self.temp_df['TP']=np.nan
        self.temp_df['SL']=np.nan
        pass
    def Stop_Hit(self,ExitPrice,EntryPrice,Low,High,Position):
##############################################################################################################
# Assume all position exited with a slippage*tick_size
# as we may not know which direction it will go first, stop out is chosen to be the conservative first direction
# Slippage will be applied to Stop loss
############################################## SL ###########################################################
       if Position==1:
           #print(f"Exit:{ExitPrice}")
           if Low<=ExitPrice['SL']:
               self.PL = Position * (ExitPrice['SL'] - EntryPrice) - self.Slippage
           
               return initialise_setting()
           else:
               return EntryPrice,ExitPrice,Position
       elif Position==-1:
           #print(f"Exit:{ExitPrice}")
           if High>=ExitPrice['SL']:
               self.PL = Position * (ExitPrice['SL'] - EntryPrice) - self.Slippage

               return initialise_setting()
           else:
               return EntryPrice,ExitPrice,Position
       elif  Position==0:
           return initialise_setting()
                  
            
    def TP_hit(self,ExitPrice,EntryPrice,Low,High,Position):
        if Position==1:
           if High>=ExitPrice['TP']:
               self.PL = Position * (ExitPrice['TP'] - EntryPrice)
           
               return initialise_setting()
           else:
               return EntryPrice,ExitPrice,Position
        elif Position==-1:
           if Low<=ExitPrice['TP']:
               self.PL = Position * (ExitPrice['TP'] - EntryPrice)

               return initialise_setting()
           else:
               return EntryPrice,ExitPrice,Position
        elif  Position==0:
        
            return initialise_setting()
        
        
        
    def reverse(self,Position,Close):
        
        
        pass
    def New_position(self,i,ExitPrice,EntryPrice,Position,Close):
        if self.temp_df["Actions"].iloc[i] == "BUY":
            if Position == 1: # if alrdy long nothing change
                return EntryPrice,ExitPrice,Position
            
            else:
                
                if Position == -1:
                    self.PL = Position * (Close - EntryPrice)
                    
                    if self.Uni_Direction == -1 : # if Uni directional , do not enter new position
                        EntryPrice,ExitPrice,Position=initialise_setting()
                        return EntryPrice,ExitPrice,Position
                   
                # if 0 position and non unidirection , do a new position with exits
                EntryPrice = Close
                SL = Close - self.tick_size * self.Stop
                Tp = Close + self.tick_size * self.TP
                
                self.temp_df["TP"].iloc[i]=Tp
                self.temp_df['SL'].iloc[i]=SL
                
                ExitPrice={'SL': SL ,
                           "TP": Tp}
                Position = 1
                return EntryPrice,ExitPrice,Position
            

        elif self.temp_df["Actions"].iloc[i] == "SELL":
            if Position == -1: # if alrdy long nothing change
                return EntryPrice,ExitPrice,Position
            
            else:
                if Position == 1:
                    self.PL = Position * (Close - EntryPrice)
                    
                    if self.Uni_Direction == 1 : # if Uni directional , do not enter new position
                        EntryPrice,ExitPrice,Position=initialise_setting()
                        return EntryPrice,ExitPrice,Position
                    
                # if 0 position and non unidirection , do a new position with exits
                EntryPrice = Close
                SL = Close + self.tick_size * self.Stop
                Tp = Close - self.tick_size * self.TP
                
                self.temp_df["TP"].iloc[i]=Tp
                self.temp_df['SL'].iloc[i]=SL
                
                ExitPrice={'SL': SL ,
                           "TP": Tp}
                Position = -1
                return EntryPrice,ExitPrice,Position
            
        else:
            return EntryPrice,ExitPrice,Position
    
    def Backtest(self):
        '''
        temp_df  : accept DataFrame with columen:CLOSE	HIGH	LOW	OPEN	VOLUME index : datetime object 
        Stops=10 : int : number of tick to hit stop from entry price
        Troubleshoot=False : Boolean : setting to True will also return the source dataframe along with  the summary
        TP_list=[20,30] : list of length 2 : a pair of targets for from the entry calculated in number of ticks, to set a single target
                                , put leave the TP_list[1] empty and set TP_size to 1
        TP_size=0.5 : float : The proportion of current total position to exit when TP_list[0] reach, set to 1 if exiting all at TP_list[0]
        tick_size=0.5: float :  the smallest move available in the asset    
        Slippage=1 : int : the number of ticks to acct of slippage when hitting the Stops
        tier_size=1 : int : the number of assset to buy on each signal 
        CAGR_N=1 : flaot : in number of years, eg 6month ==0.5 
        '''
        
        self.temp_df['prev_sign']=self.temp_df['sign'].shift()
        self.temp_df['periods']=np.nan
        self.temp_df['EntryP']=np.nan   
        self.temp_df['Stop']=np.nan
        self.temp_df['TPs']=np.nan
    
        EntryPrice,ExitPrice,Position=initialise_setting()
        self.temp_df['PL']=0
        
        # Loop Thru the Dataframe
        for i in range(self.temp_df.shape[0]):
            print(f"Row: {i}/{self.temp_df.shape[0]-1}",end='\r')
            self.PL=0

            Close=self.temp_df.iloc[i,self.temp_df.columns.str.upper().get_loc("CLOSE")]
            High=self.temp_df.iloc[i,self.temp_df.columns.str.upper().get_loc("HIGH")]
            Low =self.temp_df.iloc[i,self.temp_df.columns.str.upper().get_loc("LOW")]
            OPEN=self.temp_df.iloc[i,self.temp_df.columns.str.upper().get_loc("OPEN")]
    
    ###########################################SL and TP check##########################################
    # Assume all position exited with a slippage*tick_size
    # as we may not know which direction it will go first, stop out is chosen to be the conservative first direction
    
    ############################################## SL ######################################
        # Stop_hit(ExitPrice,EntryPrice,Low,High,Position) 
        # - if Stops hit
        #     - LowExitPrice,EntryPrice,,High,Position will be re-initialized 
        #     - self.PL = Position * (ExitPrice['Stop'] - EntryPrice) - self.Slippage
        # Else it will return the input value for ExitPrice,EntryPrice,Low,High,Position    
        
            EntryPrice,ExitPrice,Position = self.Stop_Hit(ExitPrice,EntryPrice,Low,High,Position)
            
################################################ TP ###############################################     
# TP_hit(ExitPrice,EntryPrice,Low,High,Position) 
        # - if Stops hit
        #     - LowExitPrice,EntryPrice,,High,Position will be re-initialized 
        #     - self.PL = Position * (ExitPrice['Stop'] - EntryPrice) - self.Slippage
        # Else it will return the input value for ExitPrice,EntryPrice,Low,High,Position         
            EntryPrice,ExitPrice,Position = self.TP_hit(ExitPrice,EntryPrice,Low,High,Position)
            
            EntryPrice,ExitPrice,Position = self.New_position(i,ExitPrice,EntryPrice,Position,Close)
            
            
            
            
            
            
            
            # CLOSE ALL at last period
            if i==self.temp_df.shape[0]-1:
                if Position!=0:
                    self.PL = Position * (Close - EntryPrice)
                    
            # Append the PL for this Epoch to the List later to become the PL column
            self.PL_list.append(self.PL)
            
            

 ######################## Outside for loop calculate summaries ###############################################
        self.temp_df['PL']=self.PL_list
        self.temp_df['Cumm_PL']=self.temp_df['PL'].cumsum()
    
        # adding to summary data to a Dataframe
        
        Summary_dict=S.summary(self.temp_df.PL,ref_price=self.temp_df['OPEN'].iloc[0],n=self.CAGR_N).Summary_dict
        Summary_dict['Period']='Start: '+str(self.temp_df.index[0])+' End: '+str(self.temp_df.index[-1])
        Summary_dict['NO. of Buy signal']=self.temp_df['Actions'][self.temp_df['Actions']=='BUY'].count()
        Summary_dict['NO. of Sell signal']=self.temp_df['Actions'][self.temp_df['Actions']=='SELL'].count()
        
        
        #print(Summary_dict)
        if self.Troubleshoot== True or  self.Return_df==True:
       
            return [Summary_dict,self.temp_df]
       
        return Summary_dict
    

if __name__=="__main__":
    Starttime=datetime.now()
    df= pd.read_csv("test_data.csv")
    print(f"{pd.isna(df['Actions'].iloc[4])}, ashdajd")

    x = Backtester(df,Troubleshoot=(True))
    summ,df=x.Backtest()
    breakpoint()
    df.to_csv('Test1.csv')