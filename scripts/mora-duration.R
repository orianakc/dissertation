library(lme4)
library(languageR)
library(plyr)
library(ggplot2)
library(reshape2)
library(scales)
library(arm)
library(boot)
library(lmerTest)
library(xtable)
setwd("~/dissertation/data")
dfA = read.csv("moraDuration-A.tdf",sep="\t")
dfD = read.csv("moraDuration-D.tdf",sep="\t")
dfR = read.csv("moraDuration-R.tdf",sep="\t")
dfS = read.csv("moraDuration-S.tdf",sep="\t")
dfDuration = rbind(dfA,dfD,dfR,dfS)
dfXML = read.csv("CSJ/CSJ-xml-data.csv",sep="\t")

meanDurations <- ddply(dfDuration,.(MoraEntity),summarise,avgDur=mean(MoraDuration),obs = length(MoraDuration), sd = sd(MoraDuration))

df <- merge(dfXML,meanDurations[,c(1,2)],by="MoraEntity")
colnames(df)

newDf <- merge(cc,df,by='')







