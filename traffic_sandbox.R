library(reshape2)
library(dplyr)

traffic <- read.csv('Traffic_Volume_Counts.csv')
collisions <- read.csv('Motor_Vehicle_Collisions_Crashes.csv')
melt_cols <- colnames(traffic)[1:7]

# get zipcode from segment id in traffic table
# Probably need to manually get zipcode
traffic <- melt(traffic, value.name = "volume", id = melt_cols)

# join on zipcode and time

# get street mapping attributes from https://jcoliver.github.io/learn-r/017-open-street-map.html

# this might help https://locatenyc.io/detail-intersection




