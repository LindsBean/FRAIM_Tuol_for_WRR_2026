
import numpy as np
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import math as math
import scipy as sc
from dateutil.relativedelta import relativedelta
from pyomo.environ import *

def cfsToTAF(x):
    return (x * 1.98211)/1000

def rampUpCurve(x):
    return 1.13**x

def rampDownCurve(x):
    return 0.97**x


def wyToDate(doWY, WY=2019):
    '''Given day of water year, returns datetime date object (with optional year input defaulting to 2019 (non-leap year))'''
    Y=WY-1
    date = dt.date(Y,10,1) + dt.timedelta(days=doWY)
    return date

def dateToWY(date, WY=0):
    '''Returns DAY OF WATER YEAR given a datetime date object - Can handle leap years '''
    FoWY = dt.date(date.year, 10, 1) if (date.month-10)>=0 else dt.date(date.year-1, 10, 1)
    return (date-FoWY).days

def getWY(date):
    '''Returns water year given a datetime date object'''
    WY = date.year + 1 if (date.month-10)>=0 else date.year
    return WY

def getSPRange(doWY_SP_start, Q_WetBFL_cfs, Q_SP_cfs, Q_DS_cfs):
    '''Returns: day [of water year] of the spring peak and day [of water year] SP stop
    Given: SP start as day [of water year], flows for Wet Baseflow, Spring peak and Dry Season Base
    
    Notes: 
        Spring start date ==  WetBFL
        SP Peak date flow < Spring Peak Mag (This is the date the exponential growth stops, may be a little bit choppy, but inconsequential)
        SP Peak +1 == Spring Peak Mag!
        SP Stop date == final day of spring ramp down
        SP Stop date + 1 == first day of dry season base flow
    
    Called by:  [Results Summary Functions] getDailyFlow() >> getDailyFlowPeriodDF >> getRangeVol
                Model itself calculates these in Constraints... '''
    #Get SP start
    dum= np.array([doWY_SP_start+j for j in range(1,301)])
    temp_mag = np.array([Q_WetBFL_cfs*1.13**j for j in range(1,301)])
    doWY_SP_peak = dum[(Q_SP_cfs-temp_mag)>=0][-1]
    #Get SP end date
    dum = np.array([doWY_SP_peak + 1 + j for j in range(1,301)]) #### THIS +1 GIVES ONE DAY OF Q SP PEAK - MATCHED IN getDailyFlow()
    temp_mag = np.array([Q_SP_cfs*0.93**j for j in range(1,301)])
    doWY_SP_stop = dum[(temp_mag-Q_DS_cfs)>=0][-1] 
    return int(doWY_SP_peak), int(doWY_SP_stop)

def getSPStart(Date_SP_peak, Q_WetBFL_cfs, Q_SP_cfs):
    dum= np.array([Date_SP_peak-j for j in range(1,301)])
    temp_mag = np.array([Q_WetBFL_cfs*1.13**j for j in range(1,301)])
    SP_start = dum[(temp_mag-Q_SP_cfs)<=0][-1]
    return SP_start

def getSPMagDaily(start_date, target_date, Q_start, Q_end, rampUp=True):
    '''Retuns the magnitude of a given day during the spring recession, other than peak date
    start_date refers to either the start_date of SP (for calculating ramp-up)or the peak of SP (for caclulating during rampdown) '''
    if rampUp:
        Q = Q_start*(1+0.13)**((target_date-start_date).days+1)
    else:
        Q = Q_start*(1-0.07)**((target_date-start_date).days-1)
    return Q

def getDailyFlow(DATE, doWY_WetBFL_start, doWY_SP_start, Q_WetPeak_cfsd, Q_WetBFL_cfs, Q_SP_cfs, Q_DS_cfs, Q_FA_cfs, Q_WetPeak_cfs=8500):
    doWY_SP_peak, doWY_SP_stop = getSPRange(doWY_SP_start, Q_WetBFL_cfs, Q_SP_cfs, Q_DS_cfs)
    wet_peak_start_delay  = 15
    wy = getWY(DATE)
    Date_SP_start = wyToDate(doWY_SP_start,wy)
    Date_SP_peak = wyToDate(doWY_SP_peak, wy)
    Date_SP_stop = wyToDate(doWY_SP_stop, wy)
    Date_WetBFL_start = wyToDate(doWY_WetBFL_start, wy)
    Date_WetPeak_start = wyToDate(doWY_WetBFL_start + wet_peak_start_delay, wy)
    wet_peak_dur = (Q_WetPeak_cfsd/(Q_WetPeak_cfs-Q_WetBFL_cfs))
    Date_WetPeak_end = Date_WetBFL_start + dt.timedelta(days=wet_peak_dur + wet_peak_start_delay) #
    SP_Peak_Dur = 2
    
    YEAR = Date_SP_peak.year
    Date_FA_start = dt.date(YEAR, 10, 15)
    Date_DS_resume = dt.date(YEAR, 10, 18)
    if (DATE >= (Date_FA_start-relativedelta(years=1)) and DATE < (Date_DS_resume-relativedelta(years=1))):
        flow = Q_FA_cfs
    elif DATE < Date_WetBFL_start:
        flow = Q_DS_cfs #Prior_year_Dry Season
    elif DATE < Date_WetPeak_end and DATE >= Date_WetPeak_start:
        flow = Q_WetBFL_cfs + (Q_WetPeak_cfsd/wet_peak_dur) #Wet Season Peak
    elif DATE < Date_SP_start:
        flow = Q_WetBFL_cfs #Wet Base Flow
    elif DATE < Date_SP_peak:
        flow = getSPMagDaily(Date_SP_start, DATE, Q_WetBFL_cfs, Q_SP_cfs, rampUp=True) #Spring rampup
    elif DATE < Date_SP_peak +dt.timedelta(days=SP_Peak_Dur):
        flow = Q_SP_cfs #Spring peak
    elif DATE <= Date_SP_stop: 
        flow = getSPMagDaily(Date_SP_peak, DATE, Q_SP_cfs, Q_DS_cfs, rampUp=False) #Spring rampdown
    elif (DATE >= Date_FA_start and DATE < Date_DS_resume):
        flow = Q_FA_cfs
    else: 
        flow = Q_DS_cfs #dry season
    return flow

def getDailyFlowPeriodDF(START_DATE, END_DATE, doWY_WetBFL_start, doWY_SP_start, Q_WetPeak_cfsd, Q_WetBFL_cfs, Q_SP_cfs, Q_DS_cfs, Q_FA_cfs):
    df = pd.DataFrame(columns=['DailyFlow_cfs'])
    delta = dt.timedelta(days=1)
    temp_date = START_DATE
    while temp_date <= END_DATE:
        flow = getDailyFlow(temp_date, doWY_WetBFL_start, doWY_SP_start, Q_WetPeak_cfsd, Q_WetBFL_cfs, Q_SP_cfs, Q_DS_cfs, Q_FA_cfs)
        temp = pd.DataFrame(flow, index=[temp_date], columns=['DailyFlow_cfs'])
        df = df.append(temp)
        temp_date += delta
    return df

def getRangeVol(START_DATE, END_DATE, doWY_WetBFL_start, doWY_SP_start, Q_WetPeak_cfsd, Q_WetBFL_cfs, Q_SP_cfs, Q_DS_cfs, Q_FA_cfs):
    df = getDailyFlowPeriodDF(START_DATE, END_DATE, doWY_WetBFL_start, doWY_SP_start, Q_WetPeak_cfsd, Q_WetBFL_cfs, Q_SP_cfs, Q_DS_cfs, Q_FA_cfs)
    volume_cfsday = df.DailyFlow_cfs.sum()
    volume_taf = cfsToTAF(volume_cfsday)
    return volume_cfsday, volume_taf

def getPreSpringDaily(DAY, doWY_WetBFL_start, doWY_SP_start, Q_WetPeak_cfsd, Q_WetBFL_cfs, Q_SP_cfs, Q_DS_cfs, Q_FA_cfs):
    if DAY < doWY_WetBFL_start:
        flow = Q_DS_cfs #Prior_year_Dry Season
    elif DAY == doWY_WetBFL_start: #IN OPTIMIZATION ONLY, all of the wet pulse volume is allocated to the first day of wet BFL
        flow = Q_WetBFL_cfs +  Q_WetPeak_cfsd #Wet Season Peak
    else:
        flow = Q_WetBFL_cfs #Wet Base Flow
    return flow

# def getSpecVol(START_DATE, END_DATE, doWY_WetBFL_start, doWY_SP_start, doWY_SP_peak, doWY_SP_stop, Q_WetPeak_cfsd, Q_WetBFL_cfs, Q_SP_cfs, Q_DS_cfs, Q_FA_cfs):
#     volume_cfs = 0
#     START_DAY = dateToWY(START_DATE)
#     END_DAY = dateToWY(END_DATE)
#     # if START_DAY < 30 or END_DAY < 300:
#     #     print('BREAK- cant handle early Fall Pulse yet or end date before end of spring')
#     temp_day = START_DAY
#     while temp_day <= doWY_SP_start:
#         flow = getPreSpringDaily(temp_day, doWY_WetBFL_start, doWY_SP_start, Q_WetPeak_cfsd, Q_WetBFL_cfs, Q_SP_cfs, Q_DS_cfs, Q_FA_cfs)
#         volume_cfs += flow
#         temp_day += 1
    
#     #calculate rampup
#     # THIS DOESNT WORK ##rampupV = (Q_WetBFL_cfs * 8.18213) * ((1.13**doWY_SP_start)-(1.13**doWY_SP_stop))
#     #THIS IS A LINEAR TEMP rampupV = ((Q_SP_cfs-Q_WetBFL_cfs)/(doWY_SP_peak-doWY_SP_start)) + Q_WetBFL_cfs
#     T_1 = doWY_SP_peak - doWY_SP_start
#     rampupV = T_1 * Q_WetBFL_cfs * (1.13**T_1)

#     volume_cfs += rampupV
    
#     #caclulate rampdown
#     # THIS DOESNT WORK #rampdownV = (Q_SP_cfs * 8.18213) * ((1.13**doWY_SP_peak)-(1.13**doWY_SP_stop))
#     #THIS IS A LINEAR TEST FUNC rampdownV = ((Q_DS_cfs-Q_SP_cfs)/(doWY_SP_stop-doWY_SP_peak)) + Q_SP_cfs
#     T_2 = doWY_SP_stop - doWY_SP_peak
#     rampdownV = T_2 * Q_SP_cfs * (0.93**T_2)
    
#     volume_cfs += rampdownV
    
#     #add in remaining dry season and Fall pulse
#     FA_dur = 3
#     DS_dur = END_DAY - doWY_SP_stop- FA_dur
#     volume_cfs += (DS_dur * Q_DS_cfs)
#     volume_cfs += (FA_dur * Q_FA_cfs)
    
#     volume_af = volume_cfs*1.983
#     volume_taf = volume_af/1000
#     return volume_taf

def getMaxSP_dowy(MAX_Q_SP_cfs,MAX_Q_WetBFL_cfs,MAX_Q_DS_cfs, dowy_SP_start):
    max_SP_dowy = dowy_SP_start + (math.ceil((np.log(MAX_Q_SP_cfs/MAX_Q_WetBFL_cfs)/np.log(1.13))) + math.ceil((np.log(MAX_Q_DS_cfs/MAX_Q_SP_cfs)/np.log(0.93))))+1
    return max
##FRAN APRIL 2022 EDITS NOT YET INCORPORATED INTO getSpecVol() 
def getSpecVol(START_DATE, END_DATE, doWY_WetBFL_start, doWY_SP_start, doWY_SP_peak, doWY_SP_stop, Q_WetPeak_cfsd, Q_WetBFL_cfs, Q_SP_cfs, Q_DS_cfs, Q_FA_cfs, MAX_SP_END):
    volume_cfs = 0 #initialize
    START_DAY = dateToWY(START_DATE)
    period = (END_DATE - START_DATE).days
    END_DAY = START_DAY + period
    if START_DAY < 30 :#or (END_DAY < 300 and END_DAY >= doWY_SP_start):
        print('Heads up! You are getting this warning because getSpecVol() cant handle early-run Fall Pulse yet...') 
    if END_DAY < 300 and END_DAY >= doWY_SP_start:
        print('This is just a reminder to double check that the spring pulse is behaving.')
    temp_day = START_DAY
    while temp_day < doWY_SP_start and temp_day <= END_DAY:
        flow = getPreSpringDaily(temp_day, doWY_WetBFL_start, doWY_SP_start, Q_WetPeak_cfsd, Q_WetBFL_cfs, Q_SP_cfs, Q_DS_cfs, Q_FA_cfs)
        volume_cfs += flow
        if temp_day <= END_DAY:
            temp_day += 1
        #print('in that while loop), pre spring volume is ' + str(volume_cfs))
    if  temp_day < MAX_SP_END and temp_day>=doWY_SP_start and temp_day <= END_DAY:# 
        #calculate rampup
        T_1 = doWY_SP_peak - doWY_SP_start #Does this double cacluate day of spring start ((see 197))
        
        #rampupV = T_1 * Q_WetBFL_cfs * (1.13**T_1)
        #Leading approximation edge overestimated: rampupV = Q_WetBFL_cfs * (-8.18213+(8.18213*(1.13**T_1)))
        rampupV = (Q_WetBFL_cfs * (-8.18213+(8.18213*(1.13**(T_1+0.5))))) - (Q_WetBFL_cfs * (-8.18213+(8.18213*(1.13**0.5))))#centeral difference method
        #rampupV = (1/math.log(1.13)) * (Q_WetBFL_cfs) * (1.13**T_1)
        #print('ramp up vol is '+str(rampupV))
        
        volume_cfs += rampupV

        #two day at SP peak        
        volume_cfs += (Q_SP_cfs * 2) 

        #caclulate rampdown
        T_2 = doWY_SP_stop - doWY_SP_peak - 1 #Does this double cacluate day of spring start ((see 197))
        # rampdownV = T_2 * Q_SP_cfs * (0.93**T_2)
        
        # rampdownV = (1/math.log(0.93)) * (Q_SP_cfs) * (1-0.93**T_2)
        #LEADING EDGE ESTIMATE: rampdownV = Q_SP_cfs * (13.7797-(13.7797*(0.93**T_2)))
        rampdownV = (Q_SP_cfs * (13.7797-(13.7797*(0.93**(T_2+0.5))))) - (Q_SP_cfs * (13.7797-(13.7797*(0.93**0.5))))#Central difference formulation 
        #print('ramp down vol is '+str(rampdownV))

        # rampdownV = (1/math.log(1.07)) * (Q_DS_cfs) * (1.07**T_2) # seems to work
        volume_cfs += rampdownV

        #remaining DS through end of   July
        DSjune_dur = MAX_SP_END - doWY_SP_start - T_1  - T_2 - 2 + 1   # minus two for peak, plus one for following DSbfl 2-day cushion
        DSjun_cfs = DSjune_dur * Q_DS_cfs # IN MAY RUN THISE USES DRY SEASON VOL FOR DECISION PERIOD, wont match stage 2... hmmmm

        volume_cfs+=DSjun_cfs
        
        temp_day = MAX_SP_END+1
    
    if END_DAY > MAX_SP_END and temp_day > MAX_SP_END:

        #add in remaining dry season a
        DS_dur = END_DAY - temp_day + 1 # (include end day of model)
        volume_cfs += (DS_dur * Q_DS_cfs)
        if END_DAY>dateToWY(dt.date(2020,10,18)):
            FA_dur = 3
            volume_cfs += (FA_dur * Q_FA_cfs)
            volume_cfs -= (Q_DS_cfs * FA_dur)

    volume_taf = cfsToTAF(volume_cfs)
    return volume_taf    


def getSpecVol_FFRI(inv_functions_dict,FFRI,START_DATE, END_DATE, doWY_WetBFL_start, doWY_SP_start, peak_dur, daily_disag=False, pyomo=False, MAX_SP_END=False):
    Q_WetBFL_cfs = inv_functions_dict['Q_WetBFL_cfs'](FFRI)
    Q_SP_cfs = inv_functions_dict['Q_SP_cfs'](FFRI)
    Q_DS_cfs = inv_functions_dict['Q_DS_cfs'](FFRI)
    Q_FA_cfs = inv_functions_dict['Q_WetBFL_cfs'](FFRI)
    Q_WetPeak_cfsd = Q_SP_cfs * peak_dur
    
    if daily_disag == True:
        sp_peak_date, sp_end_date = getSPRange(doWY_SP_start,Q_WetBFL_cfs, Q_SP_cfs, Q_DS_cfs)
        doWY_SP_peak = dateToWY(sp_peak_date)
        doWY_SP_stop = dateToWY(sp_end_date)

    if daily_disag == False:
        if pyomo == True:
            doWY_SP_peak = (log(Q_SP_cfs/Q_WetBFL_cfs)/log(1.13)) + doWY_SP_start
            doWY_SP_stop = (log(Q_DS_cfs/Q_SP_cfs)/log(0.93)) + doWY_SP_start + 1 
        else:
            doWY_SP_peak = (np.log(Q_SP_cfs/Q_WetBFL_cfs)/np.log(1.13)) + doWY_SP_start
            doWY_SP_stop = (np.log(Q_DS_cfs/Q_SP_cfs)/np.log(0.93)) + doWY_SP_start + 1 

    if MAX_SP_END == False:
        MAX_SP_END = getMaxSP_dowy(inv_functions_dict['Q_SP_cfs'](90),inv_functions_dict['Q_WetBFL_cfs'](90),inv_functions_dict['Q_DS_cfs'](90),doWY_SP_start)

    volume = getSpecVol(START_DATE, END_DATE, doWY_WetBFL_start, doWY_SP_start, doWY_SP_peak, doWY_SP_stop, Q_WetPeak_cfsd, Q_WetBFL_cfs, Q_SP_cfs, Q_DS_cfs, Q_FA_cfs, MAX_SP_END)

    return volume














volume_decision = getSpecVol(START_DATE=dt.date(2019, 5,1), 
                             END_DATE=dt.date(2019,6,30), 
                             doWY_WetBFL_start=dateToWY(dt.date(2020,1,18)), 
                             doWY_SP_start=dateToWY(dt.date(2020,5,3)), 
                             doWY_SP_peak=234, 
                             doWY_SP_stop=275, 
                             Q_WetPeak_cfsd=77500, 
                             Q_WetBFL_cfs=750, 
                             Q_SP_cfs =8500, 
                             Q_DS_cfs=450, 
                             Q_FA_cfs=2000,
                             MAX_SP_END= 365)
volume_therest = getSpecVol(START_DATE=dt.date(2019,12,31), 
                            END_DATE=dt.date(2020,11,30), 
                            doWY_WetBFL_start=dateToWY(dt.date(2020,1,18)), 
                            doWY_SP_start=dateToWY(dt.date(2020,5,3)), 
                             doWY_SP_peak=234, 
                             doWY_SP_stop=275, 
                             Q_WetPeak_cfsd=77500, 
                             Q_WetBFL_cfs=750, 
                             Q_SP_cfs =8500, 
                             Q_DS_cfs=450, 
                             Q_FA_cfs=2000,
                             MAX_SP_END= 365)
    
    
from importFunctions_TUOL import channelCapacityAdj_Tuol, getSpringStartTiming, WET_MAG_ADJ,SP_MAG_ADJ,DS_MAG_ADJ




# def getSpecVol(START_DATE, END_DATE, doWY_WetBFL_start, doWY_SP_start, doWY_SP_peak, doWY_SP_stop, Q_WetPeak_cfsd, Q_WetBFL_cfs, Q_SP_cfs, Q_DS_cfs, Q_FA_cfs, pyomo=False):
#     volume_cfs = 0 #initialize
#     START_DAY = dateToWY(START_DATE)
#     period = (END_DATE - START_DATE).days
#     END_DAY = START_DAY + period
#     if START_DAY < 30 or (END_DAY < 300 and END_DAY >= doWY_SP_start):
#         print('BREAK- cant handle early Fall Pulse yet or end date before end of spring')
#     temp_day = START_DAY
#     while temp_day <= doWY_SP_start and temp_day <= END_DAY:
#         flow = getPreSpringDaily(temp_day, doWY_WetBFL_start, doWY_SP_start, Q_WetPeak_cfsd, Q_WetBFL_cfs, Q_SP_cfs, Q_DS_cfs, Q_FA_cfs)
#         volume_cfs += flow
#         temp_day += 1
    
#     if END_DAY >= doWY_SP_start and temp_day <= END_DAY:
#         #calculate rampup
#         T_1 = doWY_SP_peak - doWY_SP_start #Does this double cacluate day of spring start ((see 197))
        
#         #rampupV = T_1 * Q_WetBFL_cfs * (1.13**T_1)
#         rampupV = Q_WetBFL_cfs * (-8.18213+(8.18213*(1.13**T_1)))
#         #rampupV = (1/math.log(1.13)) * (Q_WetBFL_cfs) * (1.13**T_1)

        
#         volume_cfs += rampupV

#         #one day at SP peak        
#         volume_cfs += Q_SP_cfs

#         #caclulate rampdown
#         T_2 = doWY_SP_stop - doWY_SP_peak #Does this double cacluate day of spring start ((see 197))
#         # rampdownV = T_2 * Q_SP_cfs * (0.93**T_2)
        
#         # rampdownV = (1/math.log(0.93)) * (Q_SP_cfs) * (1-0.93**T_2)
#         rampdownV = Q_SP_cfs * (13.7797-(13.7797*(0.93**T_2)))
#         # rampdownV = (1/math.log(1.07)) * (Q_DS_cfs) * (1.07**T_2) # seems to work
        
#         volume_cfs += rampdownV
        
#         #add in remaining dry season and Fall pulse
#         FA_dur = 3
#         DS_dur = END_DAY - doWY_SP_stop - FA_dur + 1 # (include end day of model)
#         volume_cfs += (DS_dur * Q_DS_cfs)
#         volume_cfs += (FA_dur * Q_FA_cfs)
    
#     volume_af = volume_cfs*1.983
#     volume_taf = volume_af/1000
#     return volume_taf    
    


# df=pd.DataFrame()
# cols=['performance10', 'performance50', 'performance90']
# idx=[10,50,90]

# for i in range(len(cols)):
#     n = idx[i]
#     df[cols[i]] = getDailyFlowPeriodDF(START_DATE=dt.date(2019,10,1), END_DATE=dt.date(2020,9,30), doWY_WetBFL_start=rangeDict_Date_WetBFL_start[n], doWY_SP_start=rangeDict_Date_SP_start[n], Q_WetPeak_cfsd=rangeDict_Q_WetPeak_cfsd[n], Q_WetBFL_cfs=rangeDict_Q_WetBFL_cfs[n], Q_SP_cfs=rangeDict_Q_SP_cfs[n], Q_DS_cfs=rangeDict_Q_DS_cfs[n], Q_FA_cfs=rangeDict_Q_FA_cfs[n])
    

# # df = getDailyFlowPeriodDF(START_DATE=dt.date(2019,12,1), END_DATE=dt.date(2020,11,30), Date_WetBFL_start=dt.date(2020,1,20), Date_SP_peak=dt.date(2020,5,20), Q_WetPeak_cfsd=10000, Q_WetBFL_cfs=500, Q_SP_cfs=5000, Q_DS_cfs=300, Q_FA_cfs=1000)
# df.plot()

# print(getRangeVol(START_DATE=dt.date(2019,10,1), END_DATE=dt.date(2020,9,30), doWY_WetBFL_start=98, doWY_SP_start=rangeDict_Date_SP_start[50], Q_WetPeak_cfsd=10000, Q_WetBFL_cfs=500, Q_SP_cfs=5000, Q_DS_cfs=300, Q_FA_cfs=1000))

# df = pd.DataFrame()
# cols=['performance10', 'performance50', 'performance90']
# idx=[10,50,90]

# for i in range(len(cols)):
#     n = idx[i]
#     df[cols[i]] = getRangeVol(START_DATE=dt.date(2019,10,1), END_DATE=dt.date(2020,9,30), doWY_WetBFL_start=rangeDict_Date_WetBFL_start[n], doWY_SP_start=rangeDict_Date_SP_start[n], Q_WetPeak_cfsd=rangeDict_Q_WetPeak_cfsd[n], Q_WetBFL_cfs=rangeDict_Q_WetBFL_cfs[n], Q_SP_cfs=rangeDict_Q_SP_cfs[n], Q_DS_cfs=rangeDict_Q_DS_cfs[n], Q_FA_cfs=rangeDict_Q_FA_cfs[n])
    
# plt.figure()
# plt.plot([10,50,90],[184.23355676618812,504.367090446965,853.9976358756599])
