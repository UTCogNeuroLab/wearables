library(tidyverse)
library(lubridate)

data_dir <- "~/Box/CogNeuroLab/Wearables/data/"
fitabase <- read.csv(paste0(data_dir, "fitbit/Fitabase_sleep_all.csv"))
beiwe <- read.csv(paste0(data_dir, "fitbit/Beiwe/Beiwe_sleep_all.csv"))

length(unique(c(beiwe$subject, fitabase$subject)))

colnames(fitabase)[! colnames(fitabase) %in% colnames(beiwe)]

head(fitabase)
head(beiwe)

fitabase <- fitabase %>%
  mutate(BedTime = ymd_hms(mdy_hms(BedTime)),
         WakeTime = ymd_hms(WakeTime),
         platform = "Fitabase")

beiwe <- beiwe %>%
  mutate(BedTime = ymd_hms(BedTime),
         WakeTime = ymd_hms(WakeTime),
         platform = "Beiwe") 

d <- fitabase %>%
  select(colnames(fitabase)[colnames(fitabase) %in% colnames(beiwe)]) %>%
  arrange() %>%
  rbind(arrange(beiwe[colnames(beiwe) %in% colnames(fitabase)])) %>%
  select(subject, everything(), -X) 

check <- d %>%
  select(subject, BedTime, WakeTime)

length(unique(d$subject))

head(d)
tail(d)

write.csv(d, paste0(data_dir, "fitbit/sleep_stats_fitabase_beiwe_all.csv"))


