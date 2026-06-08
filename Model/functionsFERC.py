import datetime as dt
import pandas as pd
import numpy as np
from FFM_GeneralFunctions import getWY

def cfsToTAF(f):
    return f * 1.983 /(1000)

def afToCFSD(v):
    return v / 1.983

def date_range_interior(range1_start, range1_end, range2_start, range2_end):
    new_start = max(range1_start, range2_start)
    new_end = min(range1_end, range2_end)
    return new_start, new_end

filename = 'InputData/FERC/FERC_1951-2024.xlsx'
FERC_daily_estimate = pd.read_excel(filename, sheet_name='FINAL_FERCS_BYWYT', index_col=0, header=0)     
def getFERC_CDECWYT(start_date, end_date):
    FERC_vol_cfs = FERC_daily_estimate.loc[start_date:end_date].sum()['SUM']
    FERC_vol_taf = cfsToTAF(FERC_vol_cfs)
    return FERC_vol_taf

####
# 5-*SEASON* FERC for 'MiniMax5Season_01_2022'
####

Seasons = ['WetSeason_Peak','WetSeason_Base','SpringRecession','DrySeason_Base','FallPulse']

def getFERCVol_Season(yearType, Season):
    if Season == 'WetSeason_Peak': #on top of WetBFL
        ferc_vol = 0
    if Season == 'WetSeason_Base': #Feb1-Apr30 (ASSUMES 28 days in Feb)
        dur = 28+31+30
        if yearType == 'W' or yearType == 'AN':
            requirement_cfs = 300 #Oct 16 - May 31
        if yearType == 'BN':
            requirement_cfs = 175 #Oct 16 - May 31
        if yearType == 'D' or yearType == 'CD':
            requirement_cfs = 150 #Oct 16 - May 31
        ferc_vol = cfsToTAF(dur*requirement_cfs)
    elif Season == 'SpringRecession': #May1
        dur = 31
        if yearType == 'W' or yearType == 'AN':
            requirement_cfs = 300 #Oct 16 - May 31
            requirement_af = 89882# outmigration pulse
        if yearType == 'BN':
            requirement_cfs = 175 #Oct 16 - May 31
            requirement_af = 60027
        if yearType == 'D':
            requirement_cfs =  150#Oct 16 - May 31
            requirement_af = 37060            
        if yearType == 'CD':
            requirement_cfs =  150#Oct 16 - May 31
            requirement_af = 11091          
        ferc_vol = cfsToTAF(dur*requirement_cfs) + (requirement_af/1000)  
    elif Season == 'DrySeason_Base': #Jun1-Dec31
        dur1 = 30+31+31+30 #Jun1-Sep30
        dur2 = 15 #Oct1 - Oct15
        dur3 = 16+30+31 #Oct16-Dec31
        if yearType == 'W':
            req1_cfs = 250
            req2_cfs = 300
            req3_cfs = 300
        if yearType == 'AN':
            req1_cfs = 250
            req2_cfs = 300
            req3_cfs = 300
        if yearType == 'BN':
            req1_cfs = 75
            req2_cfs = 200
            req3_cfs = 175
        if yearType == 'D':
            req1_cfs = 75
            req2_cfs = 150
            req3_cfs = 150
        if yearType == 'CD':
            req1_cfs = 50
            req2_cfs = 100
            req3_cfs = 150
        ferc_vol = cfsToTAF(dur1*req1_cfs) + cfsToTAF(dur2*req2_cfs) + cfsToTAF(dur3*req3_cfs) 
    elif Season == 'FallPulse': #Feb1-Apr30
        if yearType == 'W' or yearType == 'AN':
            requirement_af = 5950
        if yearType == 'BN':
            requirement_af = 1736
        if yearType == 'D' or yearType == 'CD':
            requirement_af = 0
        ferc_vol = requirement_af/1000
    return ferc_vol

def getFERCRangeVol(yearType, date_start, date_end): 
    WY = getWY(date_start)  
    #Note, this CDEC_WYT code only works if the start date is within the water year, appropriate for our applications of this model. 
    if yearType == 'CDEC_WYT':
        start, end = date_range_interior(date_start, date_end, dt.date(year=WY, month=7, day=1), dt.date(year=WY+1, month=1, day=31))
        return getFERC_CDECWYT(start, end) 
    
    # day = dt.timedelta(days=1)
    # temp_day = date_start
    # volume_taf = 0
    # while temp_day < date_end:
    #     #Oct1-15 flow
    #     while temp_day >= dt.date(2020,10,1).replace(year=temp_day.year) and temp_day < dt.date(2020,10,16).replace(year=temp_day.year):
    #         # print('whil1',volume_taf)
            
    #         if yearType == 'W':
    #             req_cfs = 300
    #         elif yearType == 'AN':
    #             req_cfs = 300
    #         elif yearType == 'BN':
    #             req_cfs = 200
    #         elif yearType == 'D':
    #             req_cfs = 150
    #         elif yearType == 'CD':
    #             req_cfs = 100
    #         req_taf = cfsToTAF(req_cfs)
    #         volume_taf += req_taf
            
    #         if temp_day == date_end:
    #             break
            
    #         temp_day+=day
        
    #     #Oct 16-Dec 31
    #     while temp_day >= dt.date(2020,10,16).replace(year=temp_day.year) and temp_day < dt.date(2020,1,1).replace(year=temp_day.year+1):
    #         # print('while2',volume_taf)
            
    #         if yearType == 'W':
    #             req_cfs = 300
    #         elif yearType == 'AN':
    #             req_cfs = 300
    #         elif yearType == 'BN':
    #             req_cfs = 175
    #         elif yearType == 'D':
    #             req_cfs = 150
    #         elif yearType == 'CD':
    #             req_cfs = 150

    #         req_taf = cfsToTAF(req_cfs)
            
    #         # Attraction Pulse Flow 10/15-10/17
    #         if temp_day >= dt.date(2020,10,16).replace(year=temp_day.year) and temp_day < dt.date(2020,10,19).replace(year=temp_day.year):
    #             if yearType == 'W':
    #                 req_taf += (5950/3)/1000
    #             elif yearType == 'AN':
    #                 req_taf += (5950/3)/1000
    #             elif yearType == 'BN':
    #                 req_taf += (1736/3)/1000
    #             elif yearType == 'D':
    #                 req_taf += 0
    #             elif yearType == 'CD':
    #                 req_taf += 0
            
    #         volume_taf += req_taf
            
    #         if temp_day == date_end:
    #             break
            
    #         temp_day+=day    
    #     #Jan1- May 31  
    #     while temp_day >= dt.date(2020,1,1).replace(year=temp_day.year) and temp_day < dt.date(2020,6,1).replace(year=temp_day.year):
    #         # print('while3',volume_taf)
    #         req_taf = 0
            
    #         if temp_day < dt.date(2020,2,1).replace(year=temp_day.year): #NO FERC FLOWS FEB-JUNE
    #             if yearType == 'W':
    #                 req_cfs = 300
    #             elif yearType == 'AN':
    #                 req_cfs = 300
    #             elif yearType == 'BN':
    #                 req_cfs = 175
    #             elif yearType == 'D':
    #                 req_cfs = 150
    #             elif yearType == 'CD':
    #                 req_cfs = 150

    #             req_taf = cfsToTAF(req_cfs)
                
    #             # Out-migration Pulse Flow 5/1- 5/30 #Putting FERC spring flows in May
    #             if temp_day >= dt.date(2020,5,1).replace(year=temp_day.year) and temp_day < dt.date(2020,5,1).replace(year=temp_day.year) + dt.timedelta(days=31):
    #                 if yearType == 'W':
    #                     req_taf += (89882/30)/1000
    #                 elif yearType == 'AN':
    #                     req_taf += (89882/30)/1000
    #                 elif yearType == 'BN':
    #                     req_taf += (60027/30)/1000
    #                 elif yearType == 'D':
    #                     req_taf += (37060/30)/1000
    #                 elif yearType == 'CD':
    #                     req_taf += (11091/30)/1000
            
    #         volume_taf += req_taf
            
    #         if temp_day == date_end:
    #             break
            
    #         temp_day+=day
    #     # Jun1-Sept30  
    #     while temp_day >= dt.date(2020,6,1).replace(year=temp_day.year) and temp_day < dt.date(2020,10,1).replace(year=temp_day.year):
    #         # print('while4',volume_taf)
    #         req_taf = 0
            
    #         if temp_day >= dt.date(2020,7,1).replace(year=temp_day.year):
    #             if yearType == 'W':
    #                 req_cfs = 250
    #             elif yearType == 'AN':
    #                 req_cfs = 250
    #             elif yearType == 'BN':
    #                 req_cfs = 75
    #             elif yearType == 'D':
    #                 req_cfs = 75
    #             elif yearType == 'CD':
    #                 req_cfs = 50
    #             req_taf = cfsToTAF(req_cfs) 
    #         volume_taf += req_taf
            
    #         if temp_day == date_end:
    #             break
            
    #         temp_day+=day 
    #     if temp_day == date_end:
    #         return volume_taf
    # return 

print(getFERCRangeVol('D', dt.date(2020, 1, 1), dt.date(2020, 1, 31)))

def getAnnualFERCRangeVol(yearType, date_start, date_end): 
    year = date_start.year
    day = dt.timedelta(days=1)
    temp_day = date_start
    volume_taf = 0
    while temp_day < date_end:
        #Oct1-15 flow
        while temp_day >= dt.date(2020,10,1).replace(year=temp_day.year) and temp_day < dt.date(2020,10,16).replace(year=temp_day.year):
            if temp_day == date_end:
                break
            elif yearType == 'W':
                req_cfs = 300
            elif yearType == 'AN':
                req_cfs = 300
            elif yearType == 'BN':
                req_cfs = 200
            elif yearType == 'D':
                req_cfs = 150
            elif yearType == 'CD':
                req_cfs = 100
            req_taf = cfsToTAF(req_cfs)
            volume_taf += req_taf
            temp_day+=day
        
        #Oct 16-Dec 31
        while temp_day >= dt.date(2020,10,16).replace(year=temp_day.year) and temp_day < dt.date(2020,1,1).replace(year=temp_day.year+1):
            if temp_day == date_end:
                break
            elif yearType == 'W':
                req_cfs = 300
            elif yearType == 'AN':
                req_cfs = 300
            elif yearType == 'BN':
                req_cfs = 175
            elif yearType == 'D':
                req_cfs = 150
            elif yearType == 'CD':
                req_cfs = 150

            req_taf = cfsToTAF(req_cfs)
            
            # Attraction Pulse Flow 10/15-10/17
            if temp_day >= dt.date(2020,10,16).replace(year=temp_day.year) and temp_day < dt.date(2020,10,19).replace(year=temp_day.year):
                if yearType == 'W':
                    req_taf += (5950/3)/1000
                elif yearType == 'AN':
                    req_taf += (5950/3)/1000
                elif yearType == 'BN':
                    req_taf += (1736/3)/1000
                elif yearType == 'D':
                    req_taf += 0
                elif yearType == 'CD':
                    req_taf += 0
            
            volume_taf += req_taf
            temp_day+=day    
        #Jan1- May 31  
        while temp_day >= dt.date(2020,1,1).replace(year=temp_day.year) and temp_day < dt.date(2020,6,1).replace(year=temp_day.year):
            if temp_day == date_end:
                break
            elif yearType == 'W':
                req_cfs = 300
            elif yearType == 'AN':
                req_cfs = 300
            elif yearType == 'BN':
                req_cfs = 175
            elif yearType == 'D':
                req_cfs = 150
            elif yearType == 'CD':
                req_cfs = 150

            req_taf = cfsToTAF(req_cfs)
            
            # Out-migration Pulse Flow 5/1- 5/30 #Putting FERC spring flows in May
            if temp_day >= dt.date(2020,5,1).replace(year=temp_day.year) and temp_day < dt.date(2020,5,1).replace(year=temp_day.year) + dt.timedelta(days=31):
                if yearType == 'W':
                    req_taf += (89882/30)/1000
                elif yearType == 'AN':
                    req_taf += (89882/30)/1000
                elif yearType == 'BN':
                    req_taf += (60027/30)/1000
                elif yearType == 'D':
                    req_taf += (37060/30)/1000
                elif yearType == 'CD':
                    req_taf += (11091/30)/1000
            volume_taf += req_taf
            temp_day+=day
        # Jun1-Sept30  
        while temp_day >= dt.date(2020,6,1).replace(year=temp_day.year) and temp_day < dt.date(2020,10,1).replace(year=temp_day.year):
            if temp_day == date_end:
                break
            elif yearType == 'W':
                req_cfs = 250
            elif yearType == 'AN':
                req_cfs = 250
            elif yearType == 'BN':
                req_cfs = 75
            elif yearType == 'D':
                req_cfs = 75
            elif yearType == 'CD':
                req_cfs = 50
            req_taf = cfsToTAF(req_cfs) 
            volume_taf += req_taf
            temp_day+=day 
        if temp_day == date_end:
            return volume_taf
    return 


def fallQ_FERC_cfs(yearType, WY=1):
    if yearType == 'W':
        vol_af = (5950/3)
        Q_cfs = afToCFSD(vol_af) + 300
    elif yearType == 'AN':
        vol_af = (5950/3)
        Q_cfs = afToCFSD(vol_af) + 300
    elif yearType == 'BN':
        vol_af = (1736/3)
        Q_cfs = afToCFSD(vol_af) + 175
    elif yearType == 'D':
        Q_cfs = 150
    elif yearType == 'CD':
        Q_cfs = 150 
    elif yearType == 'CDEC_WYT':
        Q_cfs = getFERC_CDECWYT(dt.date(WY-1,10,16), dt.date(WY-1,10,16))
    return Q_cfs



