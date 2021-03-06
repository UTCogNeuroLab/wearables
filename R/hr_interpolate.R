# Find watch off times from heart rate data and interpolate missing steps counts
# Question: How does the way we handle missing actigraphy data affect rest-activity rhythm measures?

## TO DO:
# 1. decide how to interpolate steps data best (mean, or other function)
# 2. write a loop to perform this for all subjects 

library(lubridate)
library(ggplot2)
library(zoo)

data_dir <- "~/Box/CogNeuroLab/Wearables/data/fitbit"

# list all heart rate data files and select the first as an example
hr_files <- list.files("~/Box/CogNeuroLab/Wearables/data/fitbit/", pattern = "heartrate_1min", full.names = TRUE)
hr <- read.csv(hr_files[1])

# find fitbit data start and end times and create a sequence in 1 minute intervals
df <- c()
df$Time <- seq(mdy_hms(head(hr[,1], 1)), mdy_hms(tail(hr[,1], 1)), by = "1 min")
hr$Time <- mdy_hms(hr$Time)

# merge sequence with actual fitbit data to identify nans in hr data and associated timestamps
df2 <- merge(df, hr, by = "Time", all = T)
watch_off <- df2$Time[is.na(df2$Value)]

# calculate total time watch was off in minutes
total_time_watch_off <- sum(is.na(df2$Value))

# load in subject's activity data file
act_files <- list.files("~/Box/CogNeuroLab/Wearables/data/fitbit/", pattern = "minuteStepsNarrow", full.names = TRUE)
act_fit <- read.csv(act_files[1])
head(act_fit)
act_fit$ActivityMinute <- mdy_hms(act_fit$ActivityMinute)

# merge heart rate data and steps data
df3 <- merge(df2, act_fit, by.x = "Time", by.y = "ActivityMinute")
head(df3)
sum(is.na(df3$Value))

# step counts at times when watch was off should all be 0
df3$Steps[is.na(df3$Value)]

# set NA values for steps where HR is NA
df3$Steps <- ifelse(is.na(df3$Value), NA, df3$Steps)

# now we want to interpolate step counts at minutes when watch was off
plot_interpolation <- function(df, starttime, endtime, method = "linear", f = NA, maxgap = "none"){
  
  df3$`Steps Interpolated` <- na.approx(df$Steps,  maxgap = maxgap, method = method, f = f)
  
  df3 %>%
    filter(Time > starttime) %>%
    filter(Time < endtime) %>%
    pivot_longer(cols = c(Steps, `Steps Interpolated`), names_to = "Key") %>%
    ggplot() + 
    geom_line(aes(x = Time, y = value, color = Key), size = 2) + 
    facet_wrap(. ~ Key) + theme_classic() + theme(legend.position = "none") +
    ylab("Steps")
}

# let's try out different interpolation methods
df = df3
starttime = ymd_hms("2019-10-25 18:00:00")
endtime = ymd_hms("2019-10-25 19:00:00")

# constant, replacing NAs with median value
method = "constant"
f = 0.5
plot_interpolation(df, starttime, endtime, method, f)

# constant, replacing NAs with upper value
method = "constant"
f = 1
plot_interpolation(df, starttime, endtime, method, f)

# linear interpolation
method = "linear"
f = NA
plot_interpolation(df, starttime, endtime, method, f)

# linear interpolation with a maximum number of interpolated values
# If exceeds maximum gap, data left unchanged.
method = "linear"
f = NA
maxgap = 30 #minutes
plot_interpolation(df, starttime, endtime, method, f, maxgap)

maxgap = 60 #minutes
plot_interpolation(df, starttime, endtime, method, f, maxgap)

# interpolate method #2: find average steps at time when watch was off from other days
library(imputeTS)
plot(df$Steps, type = "l", xlab = "Time", ylab = "Steps", main = "Raw")

# summary of missing periods for which the watch was off
statsNA(df$Steps)

# mean interpolation
plot(na_mean(df$Steps, option = "mean"), 
     type = "l", xlab = "Time", ylab = "Steps", xlim = c(1500,1700), 
     main = "Mean")

# last observation carried forward
plot(na_locf(df$Steps, option = "locf"), 
     type = "l", xlab = "Time", ylab = "Steps", xlim = c(1500,1700), 
     main = "LOCF")

# next observation carried backward
plot(na_locf(df$Steps, option = "nocb"), 
     type = "l", xlab = "Time", ylab = "Steps", xlim = c(1500,1700), 
     main = "NOCB")

# linear interpolation
plot(na.interpolation(df$Steps, option = "linear"), 
     type = "l", xlab = "Time", ylab = "Steps", xlim = c(1500,1700), 
     main = "Linear")

# spline interpolation
plot(na.interpolation(df$Steps, option = "spline"), 
     type = "l", xlab = "Time", ylab = "Steps", xlim = c(1500,1700), 
     main = "Spline")


# method #2
library(dplyr)
library(reshape2)

# create new clocktime variable
df$clocktime=lubridate::hour(df$Time) + lubridate::minute(df$Time)/60
df$StepsInt <- df$Steps

# find missing data chunks
find_missing <- function(df){
  x <- df %>%
    dplyr::mutate(missing = ifelse(is.na(StepsInt), 1, 0)) %>%
    dplyr::group_by(group = cumsum(c(0, diff(missing) != 0))) %>%
    filter(missing == 1 & n() > 1) %>%
    summarize("start_missing"=min(as.character(Time)),
              "end_missing"=max(as.character(Time)),
              "length_missing"=n()) %>%
    ungroup() %>%
    select(-matches("group"))
  
  # create new cloktime variable
  x$startclock=lubridate::hour(x$start_missing) + lubridate::minute(x$start_missing)/60
  x$endclock=lubridate::hour(x$end_missing) + lubridate::minute(x$end_missing)/60
  x <- x[order(x$length_missing),] 
  return(x)
}

# this shows us the data during the missing period of interest
x <- find_missing(df$StepsInt)

# view missing data period
df %>%
  filter(Time >= ymd_hms(x$start_missing[1])) %>%
  filter(Time <= ymd_hms(x$end_missing[1]))

# now we want to loop through each missing period, interpolate, update what periods are missing, 
# and interpolate some more, using the average value from the same time period on other days 
# of recording



# note to self: check export that we have both stepsnarrow and hr minute

interpolate_steps <- function(df){
  # where df is a dataframe containing Steps by minute from fitbit
  df$clocktime=lubridate::hour(df$Time) + lubridate::minute(df$Time)/60
  
  # create new dataframe
  df$StepsInt <- df$Steps
  x <- find_missing(df)
  
  while (dim(x)[1] > 0) {
    # convert start and end times to clocktimes
    startclock=lubridate::hour(x$start_missing[1]) + lubridate::minute(x$start_missing[1])/60
    endclock=lubridate::hour(x$end_missing[1]) + lubridate::minute(x$end_missing[1])/60
    
    # get index values for missing period
    replaceindex <- which((df$Time >= ymd_hms(x$start_missing[1])) & (df$Time <= ymd_hms(x$end_missing[1])))
    
    # now we want to see the steps data during the time period of interest on all other days
    mean_steps <- df %>%
      filter(clocktime >= startclock) %>%
      filter(clocktime <= endclock) %>%
      summarise(mean_steps = mean(Steps, na.rm = T)) %>%
      unlist()
    
    # replace values with the mean steps value from all other time periods
    df$StepsInt[replaceindex] <- mean_steps
    
    # checking that we replaced them all
    missing <- df %>%
      filter(Time > ymd_hms(x$start_missing[1])) %>%
      filter(Time < ymd_hms(x$end_missing[1])) %>%
      summarise(missing = sum(is.na(StepsInt))) %>%
      unlist()
    
    if (missing > 0){
      print("error - detected missing values!")
    } else {
      print(paste0("all missing values replaced, ", sum(is.na(df$StepsInt)), " remaining"))
    }
    
    # make a plot to check that NA periods of interest are being interpolated
    
    x <- data.frame(x, seq_along(start))
    p <- df %>%
      filter(Time > ymd_hms(x$start_missing[1]) - as.difftime(5, unit="mins")) %>%
      filter(Time < ymd_hms(x$end_missing[1]) + as.difftime(5, unit="mins")) %>%
      select(Time, Steps, StepsInt) %>%
      melt(id.vars = c("Time")) %>%
      ggplot() + 
      geom_rect(data=x, inherit.aes=FALSE, aes(xmin=ymd_hms(start_missing[1]), xmax=ymd_hms(end_missing[1]), ymin=-Inf,
                                               ymax=Inf), fill="yellow", alpha=0.02) +
      geom_line(aes(x = Time, y = value, group = variable, color = variable)) + 
      facet_wrap(. ~ variable, nrow = 2) +
      scale_color_brewer(palette = "Set1") +
      theme_classic() + 
      xlab("Time") + ylab("Steps") + 
      ylim(-0.1, max(df$Steps, na.rm = T))
    
    # to do: figure out how to get these plots to print while in a while loop!
    print(p)
    
    # check for missing periods and update on each round of interpolation
    x <- find_missing(df)
    print(dim(x)[1])
  }
  
  return(df)
}


##### START HERE
#dir.create(paste0(data_dir, "interpolated/"))
out_dir <- paste0(data_dir, "/interpolated")

# write the for loop!
i = list.files(data_dir, pattern = "minuteStepsNarrow", full.names = T)[1]
act_files <- list.files(data_dir, pattern = "minuteStepsNarrow", full.names = T)
hr_files <- list.files(data_dir, pattern = "heartrate_1min", full.names = T)
# for every subject that we have fitbit data for
for (i in act_files){
  hr <- c(); df <- c(); df2 <- c(); df3 <- c(); dfInt <- c()
  
  # get subject number
  fname = strsplit(i, "/")[[1]][9]
  subject = substring(fname, 1, 8)
  
  # use hr data to id missing periods
  # TO DO!!!!
  hr_fname <- # match, %in% ## string match ## <- hr_files[!!index!!]
  hr <- read.csv(hr_fname)
  
  # find fitbit data start and end times and create a sequence in 1 minute intervals
  df <- c()
  df$Time <- seq(mdy_hms(head(hr[,1], 1)), mdy_hms(tail(hr[,1], 1)), by = "1 min")
  hr$Time <- mdy_hms(hr$Time)
  
  # merge sequence with actual fitbit data to identify nans in hr data and associated timestamps
  df2 <- merge(df, hr, by = "Time", all = T)
  #watch_off <- df2$Time[is.na(df2$Value)]
  
  # TO DO - add this in 
  # calculate total time watch was off in minutes
  # total_time_watch_off <- sum(is.na(df2$Value))
  
  # load in subject's activity data file
  # read in their fitbit data, df
  df <- read.csv(i)  
  df$ActivityMinute <- mdy_hms(df$ActivityMinute)
  
  # merge heart rate data and steps data
  df3 <- merge(df2, df, by.x = "Time", by.y = "ActivityMinute")
  
  # set NA values for steps where HR is NA
  df3$Steps <- ifelse(is.na(df3$Value), NA, df3$Steps)
  
  # check that there are NA values in steps variable now
  #sum(is.na(df3$Steps))
  
  # create df$StepsInt
  # TO DO: comment out the plot step from interpolate_steps function
  dfInt <- interpolate_steps(df3)
  
  # just keep Time and StepsInt from df3
  dfInt <- dfInt %>%
    select(Time, StepsInt)
  
  dfInt$Time <- as.character(lubridate::ymd_hms(dfInt$Time))
  
  # rename variables or remove headers completely to be compatible with cr packages
  
  # save it out as a new file without overwriting the og
  # TO DO: make our actigraphy data readable by TWO packages without duplicating data files - eg header vs no header
  write.table(dfInt, paste0(out_dir, "/", subject, "_interpolated_mean.txt"), sep = " ", row.names = F, col.names = F)

}



# graph
df %>%
  mutate(Date = lubridate::date(Time)) %>%
  mutate(Hour = strftime(Time, format="%H:%M:%S")) %>% # change this from hour to hour minute format
  select(Hour, Date, Time, Steps, StepsInt) %>%
  melt(id.vars = c("Time", "Hour", "Date")) %>%
  ggplot() + 
  geom_line(aes(x = Time, y = value, color = variable), na.rm = F) + 
  facet_wrap(. ~ variable, nrow = 2, scales = "free") +
  scale_color_brewer(palette = "Set1") +
  theme_classic() + 
  xlab("Time") + ylab("Steps") +
  ggsave("~/Box/CogNeuroLab/Wearables/results/figures/interpolated_ts_fitbit.png", dpi = 300, width = 15, height = 10, units = "in")
