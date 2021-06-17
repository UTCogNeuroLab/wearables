library(readr)
library(stringr)

redcap <- read_csv("~/Box/CogNeuroLab/Wearables/data/sleep_diaries/WearableAssessment-SleepSurveys_DATA_2021-06-17_1615.csv")
qualtrics <- read_csv("~/Box/CogNeuroLab/Wearables/data/sleep_diaries/qualtrics_sleep_survey.csv", col_names= F)

colnames(qualtrics) <- qualtrics[2,]

qualtrics_n <- qualtrics %>%
  mutate_all(as.character) %>%
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
         wakeup_time = `What time did you wake up this morning? (HH:MM)`,
         sleep_quality = `How well did you sleep last night?`,
         n_watch_off = `How many times did you remove the activity band(s) yesterday?`) %>%
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
         wakeup_time,
         sleep_quality,
         n_watch_off)

redcap_n <- redcap %>%
  mutate_all(as.character) %>%
  rename(sleep_quality = sleep_quality_f4be7b_v2,
         bed_time = bed_time_0fbbb9,
         timestamp = daily_sleep_survey_timestamp) %>%
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
         wakeup_time,
         sleep_quality,
         n_watch_off) %>%
  drop_na(bed_time)

redcap_cov <- redcap %>%
  select(record_id,
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
  mutate_all(as.character)

redcap_cov <- redcap_cov %>%
  rename_with(~ sub("_v2$", "", .x), everything()) %>%
  rename(bed_time = bed_time_0fbbb9,
         sleep_quality = sleep_quality_f4be7b,
         timestamp = daily_sleep_survey_2_timestamp)

d <- rbind(redcap_n, qualtrics_n)
d <- rbind(d, redcap_cov)

head(d)

write.csv(d, '~/Box/CogNeuroLab/Wearables/data/sleep_diaries/sleep_diaries_all.csv', row.names = F)

