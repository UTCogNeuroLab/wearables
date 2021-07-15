library(readr)
library(stringr)

redcap <- read_csv("~/Box/CogNeuroLab/Wearables/data/sleep_diaries/WearableAssessment-SleepSurveys_DATA_2021-06-24_1200.csv")
qualtrics <- read_csv("~/Box/CogNeuroLab/Wearables/data/sleep_diaries/qualtrics_sleep_survey.csv", col_names= F)

colnames(qualtrics) <- qualtrics[2,]

qualtrics_n <- qualtrics %>%
  rename(record_id = Subject,
         timestamp = `Start Date`,
         bed_time = `What time did you get into bed last night? (HH:MM)`,
         sleep_time = `What time did you attempt to fall asleep last night? (HH:MM)`,
         sleep_minutes = `How long (in minutes) did it take you to fall asleep last night?`,
         wakeups = `How many times did you wake up during the night?`,
         awakening1_time = `Please list the time and duration of your awakening during the night. - When was the first time you woke up? - Awakening #1 - Time (HH:MM)`,
         awakening1_length = `Please list the time and duration of your awakening during the night. - How long (in minutes) were you awake? - Awakening #1 - Minutes`,
         awakening2_time =  `Please list the time and duration of your awakening during the night. - When was the next time you woke up? - Awakening #2 - Time (HH:MM)`,
         awakening2_length = `Please list the time and duration of your awakening during the night. - How long (in minutes) were you awake? - Awakening #2 - Minutes`,
         awakening3_time = `Please list the time and duration of your awakening during the night. - When was the next time you woke up? - Awakening #3 - Time (HH:MM)`,
         awakening3_length = `Please list the time and duration of your awakening during the night. - How long (in minutes) were you awake? - Awakening #3 - Minutes`,
         awakening4_time = `Please list the time and duration of your awakening during the night. - When was the next time you woke up? - Awakening #4 - Time (HH:MM)`,
         awakening4_length = `Please list the time and duration of your awakening during the night. - How long (in minutes) were you awake? - Awakening #4 - Minutes`,
         awakening5_time = `Please list the time and duration of your awakening during the night. - When was the next time you woke up? - Awakening #5 - Time (HH:MM)`,
         awakening5_length = `Please list the time and duration of your awakening during the night. - How long (in minutes) were you awake? - Awakening #5 - Minutes`,
         wake_time = `What time did you wake up this morning? (HH:MM)`,
         sleep_quality = `How well did you sleep last night?`,
         n_watch_off = `How many times did you remove the activity band(s) yesterday?`) %>%
  filter(!grepl('test|Subject', record_id)) %>%
  filter(!grepl('ImportI', record_id)) %>%
  mutate_at(vars(ends_with("time")), ~paste0(str_pad(., width = 5, pad = "0"), ":00"), ~na_if(., "NA:00")) %>%
  mutate_at(vars(ends_with("time")), ~na_if(., "NA:00")) %>%
  select(record_id,
         timestamp,
         bed_time,
         sleep_time,
         sleep_minutes,
         wakeups,
         awakening1_time,
         awakening1_length,
         awakening2_time,
         awakening2_length,
         awakening3_time,
         awakening3_length,
         awakening4_time,
         awakening4_length,
         awakening5_time,
         awakening5_length,
         wake_time,
         sleep_quality,
         n_watch_off) %>%
  mutate_all(as.character) %>%
  group_by(record_id) %>%
  mutate(event_name = row_number()) %>%
  arrange(record_id) 
  
head(qualtrics_n$wake_time)

redcap_n <- redcap %>%
  filter(grepl('[1-9]', record_id)) %>%
  mutate(record_id = ifelse(age_group == 1, paste0(1, str_pad(record_id, 4, pad = "0")), record_id)) %>%
  mutate(record_id = ifelse(age_group == 2, paste0(2, str_pad(record_id, 4, pad = "0")), record_id)) %>%
  fill(record_id,  .direction = "down") %>%
  filter(nchar(record_id) == 5) %>%
  filter(grepl('day', redcap_event_name)) %>%
  select_if(function(x) any(!is.na(x))) %>%
  mutate(event_name = str_split_fixed(redcap_event_name, "_", 3)[,2]) %>%
  mutate_all(as.character) %>%
  rename(sleep_quality = sleep_quality_f4be7b_v2,
         bed_time = bed_time_0fbbb9,
         timestamp = daily_sleep_survey_timestamp,
         wake_time = wakeup_time) %>%
  select(record_id,
         event_name,
         timestamp,
         bed_time,
         sleep_time,
         sleep_minutes,
         wakeups,
         awakening1_time,
         awakening1_length,
         awakening2_time,
         awakening2_length,
         awakening3_time,
         awakening3_length,
         awakening4_time,
         awakening4_length,
         awakening5_time,
         awakening5_length,
         wake_time,
         sleep_quality,
         n_watch_off) %>%
  drop_na(bed_time)

head(redcap_n$wake_time)

redcap_cov <- redcap %>%
  filter(grepl('[1-9]', record_id)) %>%
  mutate(record_id = ifelse(age_group == 1, paste0(1, str_pad(record_id, 4, pad = "0")), record_id)) %>%
  mutate(record_id = ifelse(age_group == 2, paste0(2, str_pad(record_id, 4, pad = "0")), record_id)) %>%
  fill(record_id,  .direction = "down") %>%
  filter(nchar(record_id) == 5) %>%
  filter(grepl('day', redcap_event_name)) %>%
  mutate(event_name = str_split_fixed(redcap_event_name, "_", 3)[,2]) %>%
  select(record_id,
         event_name,
         daily_sleep_survey_2_timestamp,
         bed_time_0fbbb9_v2,
         sleep_time_v2,
         sleep_minutes_v2,
         wakeups_v2,
         awakening1_time_v2,
         awakening1_length_v2,
         awakening2_time_v2,
         awakening2_length_v2,
         awakening3_time_v2,
         awakening3_length_v2,
         awakening4_time_v2,
         awakening4_length_v2,
         awakening5_time_v2,
         awakening5_length_v2,
         wakeup_time_v2,
         sleep_quality_f4be7b_v2,
         n_watch_off) %>%
  mutate_all(as.character) %>%
  rename_with(~ sub("_v2$", "", .x), everything()) %>%
  rename(bed_time = bed_time_0fbbb9,
         sleep_quality = sleep_quality_f4be7b,
         timestamp = daily_sleep_survey_2_timestamp,
         wake_time = wakeup_time) %>%
  drop_na(bed_time)

head(redcap_cov$wake_time)

d <- rbind(redcap_n, qualtrics_n)
d <- rbind(d, redcap_cov)

# this assumes that people filled out their survey for the night before the timestamp, and didn't miss data. will need to go through and check these
d <- d %>%
  filter(rowSums(is.na(.)) != ncol(.)-2) %>%
  drop_na(bed_time) %>%
  mutate(bed_time = ifelse(as.numeric(substr(d$bed_time, 0, 1)) < 1,
       paste(as_date(d$timestamp, "%Y-%m-%d"), d$bed_time),
       paste(as_date(d$timestamp, "%Y-%m-%d")-days(1), d$bed_time)),
       sleep_time = ifelse(as.numeric(substr(d$sleep_time, 0, 1)) < 1,
                         paste(as_date(d$timestamp, "%Y-%m-%d"), d$sleep_time),
                         paste(as_date(d$timestamp, "%Y-%m-%d")-days(1), d$sleep_time)),
       wake_time = paste(as_date(d$timestamp, "%Y-%m-%d"), d$wake_time))


d %>%
  select(bed_time, sleep_time, wake_time) %>%
  head()

write.csv(d, '~/Box/CogNeuroLab/Wearables/data/sleep_diaries/sleep_diaries_all.csv', row.names = F)
