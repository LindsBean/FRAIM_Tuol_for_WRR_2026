import datetime as dt
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from importFunctions_TUOL import channelCapacityAdj_Tuol, getSpringStartTiming, WET_MAG_ADJ,SP_MAG_ADJ,DS_MAG_ADJ, PEAK_MAG, FA_MAG_ADJ
from FFM_GeneralFunctions import getWY, wyToDate, dateToWY, getSPStart


Tuol_FFM_df = pd.read_csv('InputData/FFM_data/clean_summary_ffc_percentile_ann_vol_table.csv')
Tuol_FFM_df = channelCapacityAdj_Tuol(Tuol_FFM_df)
Tuol_FFM_df.to_csv('adjusted_df.csv')
Tuol_FFM_df = getSpringStartTiming(Tuol_FFM_df)
# Tuol_FFM_df = getSpringStartTiming(Tuol_FFM_df)


def plotPerformance(df, X, MIN, MAX, TITLE): ##TO DO - ad a linear regression computation for the FFRI function and the points
    
    m, b = np.polyfit(Tuol_FFM_df[X],Tuol_FFM_df['ann_vol_percentile'],1)
    x = np.arange(np.min(df[X].values),np.max(df[X].values),1)
    m_1, b_1 = np.polyfit([MIN,MAX],[10,90],1)
    plt.figure(tight_layout=True, figsize=[5,5])

    ax = plt.gca()
    ax.yaxis.set_label_position("right")
    ax.yaxis.tick_right()
    # ax.scatter(Tuol_FFM_df[X],(Tuol_FFM_df['ann_vol_percentile']/100),s = 5, color = 'b', label = 'Channel-adjusted data points')
    # #plt.plot(x, m*x +b, label='linear fitline')
    x_ffri = np.arange(MIN,MAX,1)
    ax.plot(x_ffri, (m_1*x_ffri + b_1)/100, label='FFRI-magnitude function')
    sns.despine(top=True, right=False)
    #plt.title(TITLE + ' Fit Comparison')
    plt.axhline(0.1, color='r', linestyle=(5,(5,10)), label='FFRI 10 and 90')
    plt.axhline(0.9, color='r', linestyle=(5,(5,10)))
    if 'Dry Season' in TITLE:
        plt.legend(loc='lower right', framealpha=1)
    
    plt.title(TITLE + '\nFFRI-Flow Relationship')
    plt.xlim(MIN-((MAX-MIN)/10), MAX+((MAX-MIN)/10))

    plt.ylim(0,1)

    ax.set_ylabel('Annual volume percentile')
    ax.set_xlabel('Flow magnitude (cfs)')
    
    secax = ax.secondary_yaxis('left', functions=(lambda x:x*100, lambda x: x))
    secax.set_ylabel('Functional Flow Regime Index (FFRI)')
    secax.set_yticks(np.arange(0, 110, 10))
    plt.savefig('Output/misc_figs/'+X+'_performance_noPts.jpg')



def plotPerformance_flip(df, X, MIN, MAX, TITLE): ##TO DO - ad a linear regression computation for the FFRI function and the points
    
    m, b = np.polyfit(Tuol_FFM_df[X],Tuol_FFM_df['ann_vol_percentile'],1)
    x = np.arange(np.min(df[X].values),np.max(df[X].values),1)
    m_1, b_1 = np.polyfit([MIN,MAX],[10,90],1)
    plt.figure(tight_layout=True, figsize=[9,5])

    ax = plt.gca()
    ax.xaxis.set_label_position("bottom")
    ax.xaxis.tick_bottom()
    if 'Spring' in TITLE: ax.scatter((Tuol_FFM_df['ann_vol_percentile']/100),Tuol_FFM_df[X],s = 5, color = 'b', label = 'Channel-adjusted natural metric data')
    else: ax.scatter((Tuol_FFM_df['ann_vol_percentile']/100),Tuol_FFM_df[X],s = 5, color = 'b', label = 'Natural metric data')
    # #plt.plot(x, m*x +b, label='linear fitline')
    x_ffri = np.arange(MIN,MAX,1)
    ax.plot( (m_1*x_ffri + b_1)/100, x_ffri, label='FFRI-magnitude function')
    sns.despine(top=False, right=True)
    #plt.title(TITLE + ' Fit Comparison')
    plt.axvline(0.1, color='r', linestyle=(5,(5,10)), label='FFRI 10 and 90')
    plt.axvline(0.9, color='r', linestyle=(5,(5,10)))
    plt.legend(loc='lower right', framealpha=1)
    
    plt.title(TITLE + ' FFRI-Flow Relationship')
    plt.ylim(0, MAX+((MAX-MIN)/10))

    plt.xlim(0,1)

    ax.set_xlabel('Annual volume percentile')
    ax.set_ylabel('Flow magnitude (cfs)')
    
    secax = ax.secondary_xaxis('top', functions=(lambda x:x*100, lambda x: x))
    secax.set_xlabel('\nFunctional Flow Regime Index (FFRI)')
    secax.set_xticks(np.arange(0, 100, 10))
    plt.savefig('Output/misc_figs/'+X+'_performance_noPts_flip.jpg')


def plotPerformanceCMS(df, X, MIN, MAX, TITLE):
    
    m, b = np.polyfit(Tuol_FFM_df[X]/10,Tuol_FFM_df['ann_vol_percentile'],1)
    x = np.arange(MIN/10,MAX/10,1)
    m_1, b_1 = np.polyfit([MIN/10,MAX/10],[10,90],1)
    plt.figure()
    plt.scatter(Tuol_FFM_df[X]/10,Tuol_FFM_df['ann_vol_percentile'],s = 5, color = 'b', label = 'Channel-adjusted data points')
    #plt.plot(x, (m*x +b), label='linear fitline')
    plt.plot(x, (m_1*x + b_1), label='Linear fit 10th-90th percentile range')
    #plt.title(TITLE + ' Fit Comparison')
    plt.legend()
    plt.ylim(0,100)
    plt.yticks(np.arange(0, 100+1, 10.0))
    plt.ylabel('Functional Flow Regime Index')
    plt.xlabel('Spring Recession Magnitude (cms)')
    plt.savefig('Output/daily_5FFM_02_2022/performance_figs/'+X+'_performance_CMS.jpg')    
    
#Rules for Peak in cfs-d - these will occur ON TOP OF wet season base flows: (these may need to have a curve-fit eventually)
peak_33 = PEAK_MAG * 1 # at ~33rd ff index
peak_90 = PEAK_MAG * 10 #at 90 ff index
peak_10 = 1

    
rangeDict_Date_WetBFL_start = {10:145,50:98,90:80} 
rangeDict_Date_SP_peak = {10:220,50:240,90:260} 
rangeDict_Q_WetBFL_cfs = {10:WET_MAG_ADJ[10], 50:(WET_MAG_ADJ[10]+WET_MAG_ADJ[90])/2, 90: WET_MAG_ADJ[90]} 
rangeDict_Q_WetPeak_cfsd = {10:peak_10,33:peak_33, 50:(peak_10 + (peak_90-(10*WET_MAG_ADJ[90])))/2,90:peak_90}
rangeDict_Q_SP_cfs = {10:SP_MAG_ADJ[10], 50:(SP_MAG_ADJ[10]+SP_MAG_ADJ[90])/2, 90: SP_MAG_ADJ[90]} 
rangeDict_Q_DS_cfs = {10:DS_MAG_ADJ[10], 50:(DS_MAG_ADJ[10]+DS_MAG_ADJ[90])/2, 90: DS_MAG_ADJ[90]} 
rangeDict_Q_FA_cfs = {10:FA_MAG_ADJ[10], 50:(FA_MAG_ADJ[10]+FA_MAG_ADJ[90])/2, 90: FA_MAG_ADJ[90]}     ## need to change to 
 
rangeDict_Date_SP_start = {10:getSPStart(rangeDict_Date_SP_peak[10], rangeDict_Q_WetBFL_cfs[10], rangeDict_Q_SP_cfs[10]),50:getSPStart(rangeDict_Date_SP_peak[50], rangeDict_Q_WetBFL_cfs[50], rangeDict_Q_SP_cfs[50]),90:getSPStart(rangeDict_Date_SP_peak[90], rangeDict_Q_WetBFL_cfs[90], rangeDict_Q_SP_cfs[90])}

   
#WET SEASON START DATE 
Date_WetBFL_start_MIN = rangeDict_Date_WetBFL_start[10] #min water year type
Date_WetBFL_start_MAX = rangeDict_Date_WetBFL_start[90] #Max water year type
#plotPerformance(Tuol_FFM_df, 'Wet_Tim', Date_WetBFL_start_MIN, Date_WetBFL_start_MAX, 'Wet Season Timing')
#plotPerformance_flip(Tuol_FFM_df, 'Wet_Tim', Date_WetBFL_start_MIN, Date_WetBFL_start_MAX, 'Wet Season Timing')
def performance_Date_WetBFL_start(doWY_WetBFL_start):
    '''Takes in a Wet Base Flow start date as DAY OF WATER YEAR and returns performance'''
    m, b = np.polyfit([Date_WetBFL_start_MIN,Date_WetBFL_start_MAX],[10,90],1)
    performance = m * doWY_WetBFL_start + b
    return performance


# SPRING RECESSION *START* DATE
Date_SP_start_MIN = getSPStart(rangeDict_Date_SP_peak[10], rangeDict_Q_WetBFL_cfs[10], rangeDict_Q_SP_cfs[10])
Date_SP_start_MAX = getSPStart(rangeDict_Date_SP_peak[90], rangeDict_Q_WetBFL_cfs[90], rangeDict_Q_SP_cfs[90])
#plotPerformance(Tuol_FFM_df, 'SP_Start_Tim', Date_SP_start_MIN, Date_SP_start_MAX, 'Spring Recession Start Timing')
#plotPerformance_flip(Tuol_FFM_df, 'SP_Start_Tim', Date_SP_start_MIN, Date_SP_start_MAX, 'Spring Recession Start Timing')
def performance_Date_SP_start(doWY_SP_start):
    m, b = np.polyfit([Date_SP_start_MIN,Date_SP_start_MAX],[10,90],1)
    performance = m * doWY_SP_start + b
    return performance
# #SPRING RECESSION PEAK DATE
# Date_SP_peak_MIN = rangeDict_Date_SP_peak[10] #min water year type
# Date_SP_peak_MAX = rangeDict_Date_SP_peak[90] #Max water year type
# plotPerformance(Tuol_FFM_df, 'SP_Tim', Date_SP_peak_MIN, Date_SP_peak_MAX , 'Spring Recession Peak Timing')
# def performance_Date_SP_peak(Date_SP_peak, wateryear=np.nan):
#     '''Takes in a Spring Recession Peak date (either as date OR [Day of water year and water year]) and returns performance'''
#     if not isinstance(Date_SP_peak, dt.datetime.date):
#         Date_SP_peak = wyToDate(Date_SP_peak)
#         if Date_SP_peak > 365 or Date_SP_peak<0:
#             print('Error in converting Day of Wateryear to Datetime in performance_Date_SP_peak()')
#     wy = Date_SP_peak.year
#     SP_peak_DoWY = (Date_SP_peak - dt.datetime(wy-1, 10, 1)).days
#     m, b = np.polyfit([Date_SP_peak_MIN,Date_SP_peak_MAX],[10,90],1)
#     performance = m * SP_peak_DoWY + b
#     return performance

def low(min):
    return min#/4

## WET PEAK 
Q_WetPeak_cfsd_MIN = rangeDict_Q_WetPeak_cfsd[10]
Q_WetPeak_cfsd_MAX = rangeDict_Q_WetPeak_cfsd[90]
# plotPerformance(Tuol_FFM_df, 'Peak_Mag', Q_WetPeak_cfsd_MIN, Q_WetPeak_cfsd_MAX, 'Wet Season Base Flow')
def performance_Q_WetPeak_cfsd(Q_WetPeak_cfsd):
    m, b = np.polyfit([Q_WetPeak_cfsd_MIN,Q_WetPeak_cfsd_MAX],[10,90],1)
    performance = m * Q_WetPeak_cfsd + b
    return performance
def low_performance_Q_WetPeak_cfsd(Q_WetPeak_cfsd):
    m,b = np.polyfit([0,low(Q_WetPeak_cfsd_MIN)],[0,10],1)
    performance = m * Q_WetPeak_cfsd + b
    return performance
def piecewise_performance_Q_WetPeak_cfsd(Q_WetPeak_cfsd_low, Q_WetPeak_cfsd):
    performance = (Q_WetPeak_cfsd_low*(33/rangeDict_Q_WetPeak_cfsd[33])) + (Q_WetPeak_cfsd*((90-33)/(rangeDict_Q_WetPeak_cfsd[90]-rangeDict_Q_WetPeak_cfsd[33])))
    return performance


# WET BASE FLOW PERFORMANCE
# plotPerformance(Tuol_FFM_df, 'Wet_BFL_Mag_10_adj_cfs', WET_MAG_ADJ[10], WET_MAG_ADJ[90], 'A)  Wet Season Base Flow')
plotPerformance_flip(Tuol_FFM_df, 'Wet_BFL_Mag_10_adj_cfs', WET_MAG_ADJ[10], WET_MAG_ADJ[90], 'Wet Season Base Flow')
m2_Q_WetBFL, b2_Q_WetBFL = np.polyfit([WET_MAG_ADJ[10], WET_MAG_ADJ[90]],[10,90],1)
m1_Q_WetBFL, b1_Q_WetBFL = np.polyfit([0, low(WET_MAG_ADJ[10])],[0,10],1)
def performance_Q_WetBFL_cfs(Q_WetBFL_cfs):
    performance = m2_Q_WetBFL * Q_WetBFL_cfs + b2_Q_WetBFL
    return performance
def low_performance_Q_WetBFL_cfs(Q_WetBFL_cfs):
    performance = m1_Q_WetBFL * Q_WetBFL_cfs + b1_Q_WetBFL
    return performance
def inv_performance_Q_WetBFL_cfs(z):
    metric = (z-b2_Q_WetBFL)/m2_Q_WetBFL
    return metric

print('WetBFL_mag, m:' + str(m2_Q_WetBFL) + ' b:'+str(b2_Q_WetBFL))

# SPRING RECESSION PERFORMANCE
# plotPerformance(Tuol_FFM_df, 'SP_Mag_adj_cfs', SP_MAG_ADJ[10], SP_MAG_ADJ[90], 'B)  Spring Pulse')
plotPerformance_flip(Tuol_FFM_df, 'SP_Mag_adj_cfs', SP_MAG_ADJ[10], SP_MAG_ADJ[90], 'Spring Pulse')
m2_Q_SP, b2_Q_SP = np.polyfit([SP_MAG_ADJ[10], SP_MAG_ADJ[90]],[10,90],1)
m1_Q_SP, b1_Q_SP = np.polyfit([0, low(SP_MAG_ADJ[10])],[0,10],1)
def performance_Q_SP_cfs(Q_SP_cfs):
    performance = m2_Q_SP * Q_SP_cfs + b2_Q_SP
    return performance
def low_performance_Q_SP_cfs(Q_SP_cfs):
    performance = m1_Q_SP * Q_SP_cfs + b1_Q_SP
    return performance 
def inv_performance_Q_SP_cfs(z):
    metric = (z-b2_Q_SP)/m2_Q_SP
    return metric
print('SP_mag, m:' + str(m2_Q_SP) + ' b:'+str(b2_Q_SP))

#DRY SEASON BASE FLOW 
# plotPerformance(Tuol_FFM_df, 'DS_Mag_adj_cfs', DS_MAG_ADJ[10], DS_MAG_ADJ[90], 'C)  Dry Season Base Flow')
plotPerformance_flip(Tuol_FFM_df, 'DS_Mag_adj_cfs', DS_MAG_ADJ[10], DS_MAG_ADJ[90], 'Dry Season Base Flow')
m2_Q_DS, b2_Q_DS = np.polyfit([DS_MAG_ADJ[10], DS_MAG_ADJ[90]],[10,90],1)
m1_Q_DS, b1_Q_DS = np.polyfit([0, low(DS_MAG_ADJ[10])],[0,10],1)
def performance_Q_DS_cfs(Q_DS_cfs):
    performance = m2_Q_DS * Q_DS_cfs + b2_Q_DS
    return performance
def low_performance_Q_DS_cfs(Q_DS_cfs):
    performance = m1_Q_DS * Q_DS_cfs + b1_Q_DS
    return performance
def inv_performance_Q_DS_cfs(z):
    metric = (z-b2_Q_DS)/m2_Q_DS
    return metric
print('DS_mag, m:' + str(m2_Q_DS) + ' b:'+str(b2_Q_DS))

# FALL PULSE 
Q_FA_cfs_MIN = rangeDict_Q_FA_cfs[10]
Q_FA_cfs_MAX = rangeDict_Q_FA_cfs[90]
m2_Q_FA, b2_Q_FA = np.polyfit([Q_FA_cfs_MIN,Q_FA_cfs_MAX],[10,90],1)
m1_Q_FA, b1_Q_FA = np.polyfit([0,low(Q_FA_cfs_MIN)],[0,10],1)
# plotPerformance(Tuol_FFM_df, 'FA_Mag', Q_FA_cfs_MIN, Q_FA_cfs_MAX , 'D)  Fall Pulse')
plotPerformance_flip(Tuol_FFM_df, 'FA_Mag', Q_FA_cfs_MIN, Q_FA_cfs_MAX , 'Fall Pulse')
def performance_Q_FA_cfs(Q_FA_cfs):
    performance = m2_Q_FA * Q_FA_cfs + b2_Q_FA
    return performance
def low_performance_Q_FA_cfs(Q_FA_cfs):
    performance = m1_Q_FA * Q_FA_cfs + b1_Q_FA
    return performance
def inv_performance_Q_FA_cfs(z):
    metric = (z-b2_Q_FA)/m2_Q_FA
    return metric

print('FA_mag, m:' + str(m2_Q_FA) + ' b:'+str(b2_Q_FA))

# VALUE FUCTIONS FOR MODEL IMPORT 
def FFMRANGEDICTS():
    return rangeDict_Date_WetBFL_start,rangeDict_Date_SP_start,rangeDict_Q_WetPeak_cfsd,rangeDict_Q_WetBFL_cfs,rangeDict_Q_SP_cfs,rangeDict_Q_DS_cfs,rangeDict_Q_FA_cfs
P_FUNCTIONS = [performance_Date_WetBFL_start, performance_Date_SP_start, performance_Q_WetPeak_cfsd,performance_Q_WetBFL_cfs,performance_Q_SP_cfs,performance_Q_DS_cfs,performance_Q_FA_cfs]
INV_P_FUNCTIONS = [inv_performance_Q_WetBFL_cfs,inv_performance_Q_SP_cfs,inv_performance_Q_DS_cfs,inv_performance_Q_FA_cfs]

P_VALS_MIP = {
    'Q_WetBFL_cfs': (m1_Q_WetBFL, m2_Q_WetBFL, b2_Q_WetBFL),
    'Q_SP_cfs': (m1_Q_SP, m2_Q_SP, b2_Q_SP),
    'Q_DS_cfs': (m1_Q_DS, m2_Q_DS, b2_Q_DS),
    'Q_FA_cfs': (m1_Q_FA, m2_Q_FA, b2_Q_FA)
}

# print(P_VALS_MIP)


