import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
os.chdir(os.path.dirname(os.path.abspath(__file__))) 

# MOS = ['Dec1','Jan1','Feb1','Mar1','Apr1','May1']
WY = 2020
updateMo = 'Dec1'

   
def importB120(WY, updateMo):
    filepath = 'InputData/SJWSI_Forecasts/'+ WY +'_SJWSI_Tuolumne.xlsx'
    b120 = pd.read_excel(filepath, sheet_name=updateMo, index_col=0, skiprows=1, nrows=6) 
    b120['Percentiles'] = ['99_%ile','90_%ile','75_%ile','50_%ile','25_%ile','10_%ile']
    b120 = b120.set_index('Percentiles')
    b120['Feb-June'] = b120[['Feb','Mar','Apr','May','Jun']].sum(axis=1)
    b120['UF_40pile'] = 0.4 * b120['Feb-June']
    return b120

b120 = importB120(str(WY), updateMo)


b120.to_dict()


def importMonthlyFNF(WY):
    filepath = 'InputData/TLG65_MonthlyFNF.csv'
    df = pd.read_csv(filepath)
    df['DATETIME'] =  pd.to_datetime(df['DATE TIME'])
    df['VALUE_taf']= (df.VALUE.astype(str).str.replace('---', '0')).astype(float)/1000
    df['Year'] = df['DATETIME'].dt.year
    df['Month'] = df['DATETIME'].dt.month
    monthlyFNF = pd.pivot_table(df,index='Month',columns='Year',values='VALUE_taf',aggfunc=np.sum)
    Feb_Jun = monthlyFNF.iloc[1:6].sum()
    Feb_Jun.name = 'Feb_Jun'
    monthlyFNF = monthlyFNF.append(Feb_Jun.transpose())
    Feb_Jun_40 = monthlyFNF.iloc[12].multiply(0.4)
    Feb_Jun_40.name = '40_Feb_Jun'
    monthlyFNF = monthlyFNF.append(Feb_Jun_40.transpose())
    WY_Total =  monthlyFNF[WY].iloc[0:9].sum() + monthlyFNF[WY-1].iloc[9:12].sum()
    return monthlyFNF, WY_Total


monthlyFNF, WYTotal = importMonthlyFNF(2012)


def getUpdateMonth120(date):
    m = date.month
    if m < 12 and m > 5:
        return 'Other'
    elif m == 12:
        return 'Dec1'
    elif m == 1:
        return 'Jan1'
    elif m == 2: 
        return 'Feb1'
    elif m == 3:
        return 'Mar1'
    elif m == 4:
        return 'Apr1'
    elif m == 5: 
        return 'May1'
    









##User input from keyboard test: 

# print('Type in desired year')
# # input
# year = input()
  

# print('Select b120 update: \n[1] December 1 \n[2] January 1 \n[3] February 1 \n[4] March 1 \n[4] April 1 \n[5] May 1')
# update = input()

# # output
# print(year, update)