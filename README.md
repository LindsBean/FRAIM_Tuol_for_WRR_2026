# Tuolumne River Environmental Flow Operations Model

**Repository for:** *Forecast-Updating Reservoir Operation Planning for Environmental Flows on the Tuolumne River*
**Author:** Lindsay Murdoch, UC Davis
**Status:**  Manuscript Submission
**README written under direction with Claude

---

## Overview

This model implements a forecast-updating reservoir operations planning framework for scheduling environmental flow releases on the Tuolumne River below Don Pedro Reservoir. It translates seasonal streamflow forecasts into daily flow targets that mimic the natural functional flow regime (FFR), quantified using the **Flow Regime Index (FRI)** — a continuous 0–100 performance metric tied to the annual volume percentile of the water year.

---

## File Descriptions

### Core Model Logic

**`FFM_GeneralFunctions.py`**
Contains functions for:
- Water year date conversion utilities (`getWY`, `dateToWY`, `wyToDate`)
- Spring recession geometry — ramp-up (13%/day) and ramp-down (7%/day) curves (`getSPRange`, `getSPStart`, `getSPMagDaily`)
- Daily flow schedule generation for a full water year (`getDailyFlow`, `getDailyFlowPeriodDF`)
- Volume calculations over arbitrary date ranges (`getRangeVol`)
- Pyomo-based optimization environment (imported via `pyomo.environ`)

**`importFunctions_TUOL.py`**
Tuolumne-specific constants and channel-capacity adjustment functions. Defines:
- Channel-capacity-adjusted flow magnitude targets by percentile for each season (`WET_MAG_ADJ`, `SP_MAG_ADJ`, `DS_MAG_ADJ`, `FA_MAG_ADJ`)
- Piecewise linear interpolation functions mapping FFC metric percentiles to adjusted flow magnitudes (`Wet_adj`, `SP_adj`, `DS_adj`)
- Spring recession start/stop timing derived from log-linear ramp geometry (`getSpringStartTiming`)

**`ffmPerformanceFunctions.py`**
Defines the FRI performance functions — linear mappings from flow magnitude or timing to a 0–100 FRI score. Covers all five flow components. Key exports:
- `P_FUNCTIONS`: list of performance functions (timing and magnitude, by season)
- `INV_P_FUNCTIONS`: inverse functions mapping a target FRI score back to a required flow magnitude
- `P_VALS_MIP`: slope/intercept coefficients for use in the MIP optimization
- `FFMRANGEDICTS()`: returns dictionaries of flow/timing targets at the 10th, 50th, and 90th percentile by season

**`peakFlowRules.py`**
Governs wet-season peak flow (2-year flood) release rules based on the Feb–Jun unimpaired flow volume percentile, fit to a gamma distribution. Rules:
- < 34th percentile: no peak flow release
- 34th–50th percentile: 3-day release
- 50th–75th percentile: 5-day release
- > 75th percentile: 10-day release

**`functionsFERC.py`**
Computes FERC (Federal Energy Regulatory Commission) license flow requirements by season and water year type (W/AN/BN/D/CD). Includes fall attraction pulse and spring out-migration pulse volumes. Used as a constraint floor in operations planning.

**`functionsB120.py`**
Imports and processes B-120 seasonal runoff forecasts from the San Joaquin Water Supply Index (SJWSI), issued monthly December through May. Also imports and reshapes historical monthly full natural flow (FNF) data from the TLG gauge (CDEC station TLG65).

### Input/Output Utilities

**`outputFunctions.py`**
Utilities for writing model results to Excel workbooks using `openpyxl`, including multi-dataframe stacking and cross-workbook sheet copying via `xlwings`.

### Notebooks

**`manuscript_fig.ipynb`**
Produces publication-quality figures for the manuscript, including:
- A 4-panel FRI–metric scatter plot grid showing natural data and FRI relationship lines for all four baseflow/pulse seasons
- A "patriotic" annual hydrograph ensemble plot showing daily flow schedules across the full FRI range (10–90), color-coded by FRI score

**`misc_figures.ipynb`**
Additional exploratory and supplementary figures.

---

## Input Data

The model expects the following data files (not included in this repository):

| File | Location | Description |
|---|---|---|
| `clean_summary_ffc_percentile_ann_vol_table.csv` | `InputData/FFM_data/` | Annual FFM metric values and volume percentiles from the Functional Flows Calculator |
| `FERC_1951-2024.xlsx` | `InputData/FERC/` | Daily FERC flow estimates by water year type |
| `TLG65_MonthlyFNF.csv` | `InputData/` | Monthly full natural flow record, CDEC station TLG65 |
| `[YEAR]_SJWSI_Tuolumne.xlsx` | `InputData/SJWSI_Forecasts/` | Annual B-120 forecast files by month |

---

## Dependencies

```
pandas
numpy
scipy
matplotlib
seaborn
statsmodels
pyomo
openpyxl
xlwings
dateutil
```

Install with:
```bash
pip install pandas numpy scipy matplotlib seaborn statsmodels pyomo openpyxl xlwings python-dateutil
```

---

## Key Concepts

**Water Year (WY):** October 1 – September 30. All timing is expressed as *day of water year* (day 1 = Oct 1).

**Flow Regime Index (FRI):** A continuous performance metric (0–100) that scales each functional flow component to the annual volume percentile of the water year. An FRI of 50 corresponds to a median (50th percentile) year; FRI of 10 and 90 correspond to the 10th and 90th percentile targets respectively.

**Channel Capacity Adjustment:** Raw FFC metrics are adjusted to reflect the functional range observable at the TLG gauge given channel capacity constraints (~8,500 cfs for spring peak flows).

**Forecast-Updating:** The model is designed to update flow schedules at each B-120 forecast issuance (December through May), allowing reservoir operators to revise planned releases as the seasonal runoff outlook improves.

---

## Outputs

Model outputs are written to the `Output/` directory and include:
- Daily flow schedule time series (CSV)
- FRI performance plots by season (JPEG/PNG)
- Summary Excel workbooks with seasonal volume allocations and performance scores

---

## Contact

Lindsay Murdoch  
Department of Civil and Environmental Engineering  
University of California, Davis
