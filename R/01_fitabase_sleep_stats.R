
library(tidyverse)

data_dir <- "~/Box/CogNeuroLab/Wearables/data/"
fitabase_files <- list.files(path = paste0(data_dir, "fitbit/"), pattern = "*sleepLogInfo*", full.names = T)

length(unique(substring(str_split_fixed(fitabase_files, pattern = "WA_", 2)[,2], 0, 5)))

d <- c()
for (file in fitabase_files){
  data <- read.csv(file)
  data <- data %>%
    rename(BedTime = StartTime) %>%
    mutate(subject = substring(str_split_fixed(file, pattern = "WA_", 2)[,2], 0, 5),
           WakeTime = mdy_hms(BedTime) + minutes(MinutesAsleep))
    
  d <- rbind(d, data)
  
}
head(d)
write.csv(d, paste0(data_dir, "fitbit/Fitabase_sleep_all.csv"))
