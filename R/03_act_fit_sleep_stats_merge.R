
data_dir <- '~/Box/CogNeuroLab/Wearables/data/'
fit <- read_csv(paste0(data_dir, "fitbit/sleep_stats_fitabase_beiwe_all.csv")) #paste0(data_dir, 'fitbit/fitbitSleepStatsGroup.csv'))
actiware <- read_csv(paste0(data_dir, 'actiwatch/wa_act_combined.csv'))
actiware_cl <- read_csv(paste0(data_dir, 'actiwatch/actiware_manual_clean/wa_act_combined.csv'))

# n subjects
length(unique(fit$subject))
length(unique(actiware$subject_id))

#clean actiware datasets

clean_actiware_combined_df <- function(df, suffix) {
  TimeInBed <- df %>%
    filter(interval_type == 'REST') %>%
    select(subject_id, start_date, interval_number, duration) %>%
    rename(time_in_bed = duration)
  
  dfnew <- df %>%
    dplyr::filter(interval_type == 'SLEEP') %>%
    merge(TimeInBed, by = c('subject_id', 'start_date', 'interval_number')) %>%
    select(where(function(x) all(!is.na(x)))) %>%
    rename(
      subject = subject_id,
      sleep_duration = duration) %>%
    mutate(
      bed_time = ymd_hms(as_datetime(paste(start_date, start_time), format = '%m/%d/%Y %I:%M:%S %p')),
      wake_time = ymd_hms(as_datetime(paste(end_date, end_time), format = '%m/%d/%Y %I:%M:%S %p'))) %>%
    select(-interval_type) %>%
    mutate(join_date = format(ymd_hms(wake_time), '%Y-%m-%d'),
           redcap_id = str_pad(str_sub(subject, -3, -1), width = 3, pad = "0")) %>%
    rename_at(vars(-subject, -redcap_id, -join_date), ~ paste0(., suffix))
    
  
  return(dfnew)
}

act <- clean_actiware_combined_df(actiware, "_act")
act_cl <- clean_actiware_combined_df(actiware_cl, "_cl")


#fitbit subject numbers are different for subjects who used Beiwe, so need to match them with their full subject number from Actiware

# match date formats between fitbit and actiwatch datasets
act_cl <- act_cl %>%
  mutate(cleaned = ifelse(analysis_name_cl == "Manual", 1, 0))


fitnew <- fit %>% 
  mutate(redcap_id = str_pad(str_sub(subject, -3, -1), width = 3, pad = "0"), 
         join_date = format(ymd_hms(WakeTime), '%Y-%m-%d')) %>%
  rename(sleep_duration = MinutesAsleep, 
         time_in_bed = TimeInBed, 
         efficiency = Efficiency, 
         onset_latency = MinutesToFallAsleep, 
         awake_duration = AwakeDuration,
         wake_time = WakeTime,
         bed_time = BedTime) %>%
  select(-X1, -Duration) %>%
  rename_at(vars(-subject, -redcap_id, -join_date), ~ paste0(., '_fit')) %>%
  filter(rowSums(is.na(.)) != ncol(.)-1)


df <- merge(act, fitnew, by = c('redcap_id', 'join_date'), all = T) %>%
  rename(subject = subject.x) %>%
  select(-subject.y)

redcap <- read.csv(paste0(data_dir, "WearableAssessment-Validation_DATA_2021-01-29_1236.csv"))

rc <- redcap %>%
  filter(grepl("arm_1", redcap_event_name)) %>%
  mutate(fitbit_device = ifelse((selected_devices___3 == 1),
                                 "Fitbit Inspire HR", "Fitbit Charge 2 HR")) %>%
  select(record_id, age_group, handedness, actiwatch_arm, fitbit_device) %>%
  mutate(redcap_id = str_pad(str_sub(record_id, -3, -1), width = 3, pad = "0")) %>%
  group_by(redcap_id) %>%
  fill(age_group, handedness, .direction = "down") %>%
  drop_na(actiwatch_arm) %>%
  mutate(age_group = recode(age_group, "Young Adults", "Older Adults")) %>%
  mutate(handedness = recode(handedness, "Left", "Right", "Both")) %>%
  mutate(actiwatch_arm = recode(actiwatch_arm, "Left", "Right")) %>%
  mutate(dominant = ifelse(handedness == actiwatch_arm, 1, 0)) %>%
  ungroup() 

write.csv(rc, paste0(data_dir, 'demographics_condition_assignments.csv'))

df <- merge(rc, df, by = 'redcap_id', all = T) %>%
  select(subject, everything(), -record_id) %>%
  group_by(redcap_id) %>%
  fill(subject, .direction = "down") %>%
  ungroup()

length(unique(df$subject))

check<- df %>%
  select(subject, redcap_id, interval_number_act, bed_time_act, bed_time_fit)

unique(df$subject)

write.csv(df, file = paste0(data_dir, 'sleep_stats.csv'), row.names = F)
