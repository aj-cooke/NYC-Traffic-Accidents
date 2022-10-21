# Marcus does 1-611, Rachel does 612-1222, I do 1223-1833 and Xinming does 1834-2443
library(tidyverse)

# 1834-2443
setwd("/Users/daixinming/Documents/Graduate_School/2022_Fall/Seminar/stat_project/NYC-Traffic-Accidents/data")
traffic <- read.csv("Traffic_Volume_Counts.csv")
segments <- read.csv("segments.csv")
segments <- 
  segments %>% 
  filter(id >= 1834)
