import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.formula.api as sm
import os
os.chdir(os.path.dirname(os.path.abspath(__file__))) 

WET_MAG_ADJ = {10:344, 25:526, 50:849, 75:1378, 90:1534} # %ile:mag_cfs
SP_MAG_ADJ = {10:1250, 25:3000, 50:5000, 75:7000, 90:8500} # %ile:mag_cfs
DS_MAG_ADJ = {10:160, 25:177, 50:333, 75:383.5, 90:447}
FA_MAG_ADJ = {10:402, 25:596, 50:973, 75:1625, 90:2417}
PEAK_MAG = 8500


def channelCapacityAdj_Tuol(df):
    '''Iterates through dataframe performing channel Capacity adjustments
    input: dataframe from FFM calculator paired with annual flow volumes
    output: dataframe with channel capacity-adjusted columns
    '''
    v_Wet_adj = np.vectorize(Wet_adj)
    v_SP_adj = np.vectorize(SP_adj)
    v_DS_adj = np.vectorize(DS_adj)
    Wet_BFL_Mag_10_adj_cfs = df.Wet_BFL_Mag_10.values
    SP_Mag_adj_cfs = v_SP_adj(df.SP_Mag_pct.values)
    DS_Mag_adj_cfs = df.DS_Mag_50.values
    df2 = pd.DataFrame(zip(Wet_BFL_Mag_10_adj_cfs,SP_Mag_adj_cfs,DS_Mag_adj_cfs), columns=['Wet_BFL_Mag_10_adj_cfs','SP_Mag_adj_cfs','DS_Mag_adj_cfs'], index=df.index)
    merged = pd.merge(df,df2, left_index=True, right_index=True)
    return merged

def Wet_adj(pct):
    '''Wet Season Baseflow Adjustments
    given unadjusted mag and %ile, gives new mag adjusted for channel capacity'''
    if pct < 10:
        return WET_MAG_ADJ[10] # confirm this is minimum
    elif pct< 25: #10-25 %ile
        m = ((WET_MAG_ADJ[25]-WET_MAG_ADJ[10])/(25-10))
        b = WET_MAG_ADJ[25] - (m*25)
    elif pct< 50: #25-50 %ile
        m = ((WET_MAG_ADJ[50]-WET_MAG_ADJ[25])/(50-25))
        b = WET_MAG_ADJ[50] - (m*50)
    elif pct< 75: #50-75 %ile
        m = ((WET_MAG_ADJ[75]-WET_MAG_ADJ[50])/(75-50))
        b = WET_MAG_ADJ[75] - (m*75)
    elif pct< 90: #75-90 %ile
        m = ((WET_MAG_ADJ[90]-WET_MAG_ADJ[75])/(90-75))
        b = WET_MAG_ADJ[75] - (m*75)
    else: return WET_MAG_ADJ[90] #Double check with Sarah that this is the MAX (same as 90th percentile?)
    return  m * pct + b

def SP_adj(pct):    
    '''Spring Recession Flow Adjustments
    given unadjusted mag and %ile, gives new mag adjusted for channel capacity'''

    if pct < 10:
        return SP_MAG_ADJ[10] # confirm this is minimum
    elif pct< 25: #10-25 %ile
        m = ((SP_MAG_ADJ[25]-SP_MAG_ADJ[10])/(25-10))
        b = SP_MAG_ADJ[25] - (m*25)
    elif pct< 50: #25-50 %ile
        m = ((SP_MAG_ADJ[50]-SP_MAG_ADJ[25])/(50-25))
        b = SP_MAG_ADJ[50] - (m*50)
    elif pct< 75: #50-75 %ile
        m = ((SP_MAG_ADJ[75]-SP_MAG_ADJ[50])/(75-50))
        b = SP_MAG_ADJ[75] - (m*75)
    elif pct< 90: #75-90 %ile
        m = ((SP_MAG_ADJ[90]-SP_MAG_ADJ[75])/(90-75))
        b = SP_MAG_ADJ[90] - (m*90)
    else: return SP_MAG_ADJ[90] #Double check with Sarah that this is the MAX (same as 90th percentile?)
    return  m * pct + b



def DS_adj(pct):    
    '''Dry Season Baseflow Adjustments
    given unadjusted mag and %ile, gives new mag adjusted for channel capacity'''

    if pct < 10:
        return DS_MAG_ADJ[10] # confirm this is minimum
    elif pct< 25: #10-25 %ile
        m = ((DS_MAG_ADJ[25]-DS_MAG_ADJ[10])/(25-10))
        b = DS_MAG_ADJ[25] - (m*25)
    elif pct< 50: #25-50 %ile
        m = ((DS_MAG_ADJ[50]-DS_MAG_ADJ[25])/(50-25))
        b = DS_MAG_ADJ[50] - (m*50)
    elif pct< 75: #50-75 %ile
        m = ((DS_MAG_ADJ[75]-DS_MAG_ADJ[50])/(75-50))
        b = DS_MAG_ADJ[75] - (m*75)
    elif pct< 90: #75-90 %ile
        m = ((DS_MAG_ADJ[90]-DS_MAG_ADJ[75])/(90-75))
        b = DS_MAG_ADJ[75] - (m*75)
    else: return DS_MAG_ADJ[90] #Double check with Sarah that this is the MAX (same as 90th percentile?)
    return  m * pct + b



def testAdjFunctions():
    test = np.linspace(0,100,50)

    v_Wet_adj = np.vectorize(Wet_adj)
    v_SP_adj = np.vectorize(SP_adj)
    v_DS_adj = np.vectorize(DS_adj)
    
    plt.figure()
    plt.plot(test, v_Wet_adj(test), label='Wet Season Adj')
    plt.plot(test, v_SP_adj(test), label='Spring Rec Adj')
    plt.plot(test, v_DS_adj(test), label='Dry Season Adj')
    plt.legend()
    plt.title('Adjusted Flow Mags by percentile \nBy season')
    plt.ylabel('Magnitude (cfs)')
    plt.xlabel('FFM Metric percentile')   
    

Tuol_FFM_df = pd.read_csv('InputData/FFM_data/clean_summary_ffc_percentile_ann_vol_table.csv')
  
Tuol_FFM_df2 = channelCapacityAdj_Tuol(Tuol_FFM_df)

#Tuol_FFM_df2.to_excel('Tuolumne_adjusted.xlsx')

# testAdjFunctions()    




def getSpringStartTiming(df):
    df['SP_rUP_Dur']= np.log(df['SP_Mag_adj_cfs']/df['Wet_BFL_Mag_10_adj_cfs'])/(0.13)
    df['SP_rDOWN_Dur'] = np.log(df['DS_Mag_adj_cfs']/df['SP_Mag_adj_cfs'])/(-0.07)
    df['SP_Start_Tim'] = df['SP_Tim'] - df['SP_rUP_Dur']
    df['SP_Stop_Tim'] = df['SP_Tim'] + df['SP_rDOWN_Dur']
    return df

Tuol_FFM_df3 = getSpringStartTiming(Tuol_FFM_df2)


result = sm.ols(formula="Tuol_FFM_df3.SP_Start_Tim ~ Tuol_FFM_df3.tot_vol_acft", data=Tuol_FFM_df3).fit()
# print(result.params)
b=result.params[0]
m=result.params[1]
# print(result.summary())
# x = np.linspace(0,5000)
# plt.figure()
# plt.scatter(Tuol_FFM_df3.tot_vol_acft.values,Tuol_FFM_df3.SP_Start_Tim.values, color='blue', label='SP Calculated Start Time')
# plt.scatter(Tuol_FFM_df3.tot_vol_acft.values,Tuol_FFM_df3.SP_Tim.values, color='orange', label='SP Peak Timing')
# plt.plot(x, m*x+b, color='red', alpha=0.5, label='Start_Tim trend')
# plt.legend()
# plt.plot(x,212*np.ones(len(x)), color='black', alpha=0.2, label='May 1')
# plt.plot(x,243*np.ones(len(x)), color='black', alpha=0.6, label='June 1')
# plt.plot(x,273*np.ones(len(x)), color='black', label='July 1')
# plt.text(4500, 207, 'May 1')
# plt.text(4500, 238, 'June 1')
# plt.text(4500, 268, 'July 1')
# plt.title('Spring Recession Start Time')
# plt.xlabel('Total Annual Volume (TAF)')
# plt.ylabel('Timing (Day of Water Year)')

result = sm.ols(formula="Tuol_FFM_df3.SP_Stop_Tim ~ Tuol_FFM_df3.tot_vol_acft", data=Tuol_FFM_df3).fit()
# print(result.params)
b=result.params[0]
m=result.params[1]
# print(result.summary())
# x = np.linspace(0,5000)
# plt.figure()
# plt.scatter(Tuol_FFM_df3.tot_vol_acft.values,Tuol_FFM_df3.SP_Stop_Tim.values, color='blue', label='SP Calculated Stop Time')
# plt.scatter(Tuol_FFM_df3.tot_vol_acft.values,Tuol_FFM_df3.SP_Tim.values, color='orange', label='SP Peak Timing')
# plt.plot(x, m*x+b, color='red', alpha=0.5, label='End_Tim trend')
# plt.legend()
# plt.plot(x,212*np.ones(len(x)), color='black', alpha=0.2, label='May 1')
# plt.plot(x,243*np.ones(len(x)), color='black', alpha=0.6, label='June 1')
# plt.plot(x,273*np.ones(len(x)), color='black', label='July 1')
# plt.plot(x,304*np.ones(len(x)), color='black', label='August 1')
# plt.text(4500, 207, 'May 1')
# plt.text(4500, 238, 'June 1')
# plt.text(4500, 268, 'July 1')
# plt.text(4500, 299, 'August 1')
# plt.title('Spring Recession End Time')
# plt.xlabel('Total Annual Volume (TAF)')
# plt.ylabel('Timing (Day of Water Year)')




result = sm.ols(formula="Tuol_FFM_df3.SP_Start_Tim ~ Tuol_FFM_df3.ann_vol_percentile", data=Tuol_FFM_df3).fit()
# print(result.params)
b=result.params[0]
m=result.params[1]
# print(result.summary())
x = np.linspace(0,100)
# plt.figure()
# plt.scatter(Tuol_FFM_df3.ann_vol_percentile.values,Tuol_FFM_df3.SP_Start_Tim.values, color='blue', label='SP Calculated Start Time')
# plt.scatter(Tuol_FFM_df3.ann_vol_percentile.values,Tuol_FFM_df3.SP_Tim.values, color='orange', label='SP Peak Timing')
# plt.plot(x, m*x+b, color='red', alpha=0.5, label='Start_Tim trend')
# plt.legend()
# plt.plot(x,212*np.ones(len(x)), color='black', alpha=0.2, label='May 1')
# plt.plot(x,243*np.ones(len(x)), color='black', alpha=0.6, label='June 1')
# plt.plot(x,273*np.ones(len(x)), color='black', label='July 1')
# plt.text(4500, 207, 'May 1')
# plt.text(4500, 238, 'June 1')
# plt.text(4500, 268, 'July 1')
# plt.title('Spring Recession Start Time')
# plt.title('Spring Recession End Time')
# plt.xlabel('Total Annual Volume PERCENTILE')
# plt.ylabel('Timing (Day of Water Year)')

result = sm.ols(formula="Tuol_FFM_df3.SP_Stop_Tim ~ Tuol_FFM_df3.ann_vol_percentile", data=Tuol_FFM_df3).fit()
# print(result.params)
b=result.params[0]
m=result.params[1]
# print(result.summary())
# x = np.linspace(0,100)
# plt.figure()
# plt.scatter(Tuol_FFM_df3.ann_vol_percentile.values,Tuol_FFM_df3.SP_Stop_Tim.values, color='blue', label='SP Calculated Stop Time')
# plt.scatter(Tuol_FFM_df3.ann_vol_percentile.values,Tuol_FFM_df3.SP_Tim.values, color='orange', label='SP Peak Timing')
# plt.plot(x, m*x+b, color='red', alpha=0.5, label='End_Tim trend')
# plt.legend()
# plt.plot(x,212*np.ones(len(x)), color='black', alpha=0.2, label='May 1')
# plt.plot(x,243*np.ones(len(x)), color='black', alpha=0.6, label='June 1')
# plt.plot(x,273*np.ones(len(x)), color='black', label='July 1')
# plt.plot(x,304*np.ones(len(x)), color='black', label='August 1')
# plt.text(4500, 207, 'May 1')
# plt.text(4500, 238, 'June 1')
# plt.text(4500, 268, 'July 1')
# plt.text(4500, 299, 'August 1')
# plt.title('Spring Recession End Time')
# plt.xlabel('Total Annual Volume PERCENTILE ')
# plt.ylabel('Timing (Day of Water Year)')

