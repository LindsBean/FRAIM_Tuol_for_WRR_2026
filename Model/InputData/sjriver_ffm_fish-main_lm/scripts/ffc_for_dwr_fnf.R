library(tidyverse)
library(lubridate)
library(ffcAPIClient)
library(glue)
# change sci notation to make things readable
options(scipen = 999)
Today = Sys.Date()
# Save your Token to REnviron ---------------------------------------------

# save token in your Renviron with usethis::
# library(usethis)
# run this, then paste your code in as EFLOWS_TOKEN="yourlongtokenid"
# usethis::edit_r_environ()
# then save and close, restart R session and below should work.

# Set up Processor --------------------------------------------------------

# set/get the token for using the FFC
ffctoken <- 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmaXJzdE5hbWUiOiJMaW5kc2F5IiwibGFzdE5hbWUiOiJNdXJkb2NoIiwiZW1haWwiOiJsZW11cmRvY2hAdWNkYXZpcy5lZHUiLCJyb2xlIjoiVVNFUiIsImlhdCI6MTY3OTI1NzkyN30.zNZNf-Ygxivk3oTs4XcH1roglpKYaYXim6iKCSCJTuY'

ffcAPIClient::clean_account(ffctoken)

# Lat-Long obtained from CDEC TLG site
# gageCOMID <- ffcAPIClient::get_comid_for_lon_lat(longitude = -120.441000,
#                                                  latitude = 	37.666000) 

COMID <- 2823750L # TLG CDEC

# Import data -------------------------------------------------------------

# run function

clean_df <<- read_csv("data_clean/clean_fnf_daily_dwr_TLG_cdec_2023-03-19.csv", show_col_types = FALSE)

# Run FFC -----------------------------------------------------------------

ffc <- FFCProcessor$new()

# make clean dataframe
clean_df_ffc <- clean_df %>%
  select(flow=flow_40pct7day, date) %>% as.data.frame()
class(clean_df_ffc) # make sure it's "data.frame

ffc$flow_field = "flow_40pct7day" # name of column in your dataframe
ffc$date_field = "date" # name of column in your dataframe
ffc$date_format_string <- "%Y-%m-%d" # match format of your date

# run setup: # gives error if not dataframe, and will drop years with out data
ffc$set_up(timeseries = clean_df_ffc, token = ffctoken, comid=COMID) 

# run step one first
ffc$step_one_functional_flow_results(timeseries = clean_df_ffc,
                                     comid=COMID,
                                     token = ffctoken,
                                     output_folder = "output/40pct7day")

# Look at Results ---------------------------------------------------------

ffc$ffc_percentiles %>% View()
ffc$ffc_results %>% View()
write_csv(ffc$predicted_percentiles, file = glue("output/40pct7day/{COMID}_ffc_predicted_percentiles.csv"))

# get year range:
yr_range <- unlist(ffc$raw_ffc_results$yearRanges)

# what other stuff (SD, CV, avgAnnFlow)
ann_metrics <- map_df(ffc$raw_ffc_results$allYear, ~unlist(.x)) %>% 
  bind_cols(., "year"=yr_range) %>% 
  rename(ann_sd = 1, ann_mean_flow_cfs = 2, ann_cv = 3)

# write out 
write_csv(ann_metrics, file = glue("output/40pct7day/{COMID}_ffc_ann_metrics.csv"))
