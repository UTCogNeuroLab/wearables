#

## Preprocessing

Fitbit output is steps, not raw accelerometer data. We used the heart rate data to detect periods for which the Fitbit was not worn. Periods with missing Fitbit accelerometer data were then linearly interpolated. Threshold used for interpolation? Participants with more than XX% missing data were excluded from analysis.

### Beiwe


## Sleep summary statistics comparison

### Sleep diary assessment

% missing data per subject?

### Bed time coding

Fitbit output all times for which sleep or time in bed was coded, rather than breaking it up into primary sleep period with additional rest periods like the Actiware software does. So, we looked for Fitbit bed times which were within 60 minutes of the Actiwatch bedtime and analyzed correlations between those measures.

~/Box/CogNeuroLab/Wearables/results/diary_comparison contains graphs showing each subject's raw Actiwatch data, their Actiwatch bed/wake time, Fitbit bed/wake time, and self-reported bed/wake time for each day they participated. This also excludes data from participants who participated in the study a second time ("repeat arm") during COVID-19. The subdirectory in this folder called diary_comparison_old contains these graphs but without excluding the other "bed times", or more accurately, rest/nap times, reported by Fitbit.

bed-wake-time-comparison.csv
20108, 20113, 20115 missing sleep diary and Actiwatch data
10045, 10049, 10152, 20076, 20105, 20129, 20168, 20176, 20177, 20178, 20180, 20181, 20182, 20184  missing Fitbit data. All these subjects don't have full subject numbers in 'fitbitSleepStatsGroup.csv'

Subject 20076 was accidentally coded as 10076 by RAs. Renamed these files appropriately and should no longer be missing data.

> unique(fit$subject)
 [1] 10011 10012 10014 10016 10023 10024 10025 10033 10035 10038 10040 10045 10062 [10076] 10139 10140 10143 10144 10145
[20] 10146 10147 10148 10149 10150 [10159] 20103 20105 20108 20113 20115 20120 20122 20123 20124 20125 20127 20131 20142
[39] 20154 20155 20157   [151]   [164]
> unique(act$subject)
 [1] 10011 10012 10014 10016 10023 10024 10025 10033 10035 10038 10040 10045 [10049] 10062 10139 10140 10143 10144 10145
[20] 10146 10147 10148 10149 10150 [10152] [20076] 20103 20105 20108 20113 20115 20120 20122 20123 20124 20125 20127 [20129]
[39] 20131 20142 20154 20155 20157 [20163] [20168] [20176] [20177] [20178] [20180] [20181] [20182] [20184]
> unique(beiwe$subject)
 [1] 105  11 [151] 152 163 [164] 168 177 178 180 181 182 184  23  45

 I think 164 did not participate.
 151 withdrew.
