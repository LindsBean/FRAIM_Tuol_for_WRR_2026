'''Peak flow rules - fitting to range of available volumes 
Hi Lindsay - 
Here's a set of rules to govern the 2-year peak flow (magnitude of 8500 cfs for Tuolumne) release for now:

In 'dry' years (lower 33rd percentile, including p10 and p25), do not release a 2-year flood.    This assumes there will not be enough extra water for a 2-year flood of 1 day.  If we find that there IS enough extra water, then we might choose to release a 2-year flood for 1 day in say p20-p33 years during the wet season before the spring pulse ramp-up.  

In 'moderate' years (34th-66th percentile technically, but including p50 and p75), release a 2-year flood for 3 days (p50) or 5 days (p75) during the wet season before the spring pulse ramp-up. The spring recession peak will also serve as a high flow release but of lower magnitude and for 1 day.  

In 'wet' years (67th-99th percentile technically, but including p90), release a 2-year flood for a total of 10 days during the wet season before the the spring pulse ramp-up.  This could be 1 long event of 10 days or 2 shorter 5-day events. The spring recession peak also serves as a 2-year flood event (or close to) for 1-day (so 11 days total peak flow release).  If it's a very wet year, likely spill events will be occurring and will help to meet this requirement.  High flow releases could extend into the spring pulse window, and if so, then just need to ramp-down from spill/high flow at the 7% ramp-down rate. (i.e. if spilling or releasing high flows after May 1, ramp down at 7%).  

For all 2-year flood release events, ramp up at natural inflow rates or what operators can release, but ramp-down at 35-40% per day.  After May 1, all high flows (spring recession or spill) should ramp down at 7% per day.  

Let me know if you need more guidance or clarity on these rules.  These are essentially the same as what Ann and David included in their modeling for the Upper San Joaquin tribs (magnitudes and durations slightly adjusted for each trib) but the logic of how they implemented them was a little different as we discussed.  

Thanks, Sarah

'''
import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
from scipy import stats

df = pd.read_csv('InputData/TLG65_MonthlyFNF.csv')[:-1]
df['DATE TIME'] = pd.to_datetime(df['DATE TIME'])
df['VALUE_TAF'] = df['VALUE'].astype(int)/1000
monthlyFNF = df[['DATE TIME', 'VALUE_TAF']]

monthlyDF = pd.crosstab(monthlyFNF['DATE TIME'].dt.year, 
            monthlyFNF['DATE TIME'].dt.strftime("%b"), 
            monthlyFNF.VALUE_TAF, 
            aggfunc="sum",
            rownames=["Year"],
            colnames=["Month"])[1:]

monthlyDF['FebJun'] = monthlyDF[['Feb','Mar','Apr','May','Jun']].sum(axis=1)

param = stats.gamma.fit(monthlyDF['FebJun'], floc=0 )

#_, bins, _ = plt.hist(monthlyDF['FebJun'], 100, density=1, alpha=0.5) #this line will show plot, but does the same things as np.histogram()
_, bins = np.histogram(monthlyDF['FebJun'], bins=100, density=1)
cdf_fitted = stats.gamma.cdf(bins, *param)

# no pulse below 
idx34 = (np.abs(cdf_fitted - .34)).argmin()
p34_taf = bins[idx34]

idx50 = (np.abs(cdf_fitted - .50)).argmin()
p50_taf = bins[idx50]

idx75 = (np.abs(cdf_fitted - .75)).argmin()
p75_taf = bins[idx75]



# # PLOTTING
# plt.figure()
# _, bins, _ = plt.hist(monthlyDF['FebJun'], 20, density=1, alpha=0.5)
# pdf_fitted = stats.gamma.pdf(bins, *param)
# plt.plot(bins, pdf_fitted, color='r')
# plt.axvspan(bins.min(), p34_taf, alpha=0.3, color='ghostwhite', label= 'no peakflow')
# plt.axvspan(p34_taf, p50_taf, alpha=0.3, color='lightsteelblue', label='3-day peakflow')
# plt.axvspan(p50_taf, p75_taf, alpha=0.3, color='cornflowerblue', label='5-day peakflow')
# plt.axvspan(p75_taf, bins.max(), alpha=0.3, color='royalblue', label='10-day peakflow')
# plt.legend()
# plt.xlabel('Volume (TAF)')
# plt.ylabel('Probability')
# plt.title('Probability Density Curve\nHistorical Feb-Jun UF Volume (1901-2021)')
# plt.savefig('AdaptiveBudgetPDF_peakRules.png')

# plt.figure()
# cdf_fitted = stats.gamma.cdf(bins, *param)
# plt.plot(bins,cdf_fitted)
# plt.axvspan(bins.min(), p34_taf, alpha=0.3, color='ghostwhite', label= 'no peakflow')
# plt.hlines(.34, bins.min(), bins.max(), linestyle='--', color='black', alpha=0.1)
# plt.axvspan(p34_taf, p50_taf, alpha=0.3, color='lightsteelblue', label='3-day peakflow')
# plt.hlines(.5, bins.min(), bins.max(), linestyle='--', color='black', alpha=0.1)
# plt.axvspan(p50_taf, p75_taf, alpha=0.3, color='cornflowerblue', label='5-day peakflow')
# plt.hlines(.75, bins.min(), bins.max(), linestyle='--', color='black', alpha=0.1)
# plt.axvspan(p75_taf, bins.max(), alpha=0.3, color='royalblue', label='10-day peakflow')
# plt.legend()
# plt.xlabel('Volume (TAF)')
# plt.ylabel('Cumulative Probability')
# plt.title('Cumulative Density Curve\nHistorical Feb-Jun UF Volume (1901-2021)')
# plt.savefig('AdaptiveBudgetCDF_peakRules.png')
