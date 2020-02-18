rm(list = ls())
library(plotly)
library(readxl)
library(plyr)
library(zoo)
library(dplyr)

#CAR_070_Flow_and_Totals <- read_excel("P:/Projects-South/Environmental - Schaedler/5025-19-W006 CoSDWQ TO6 Low Flow Monitoring/DATA/GitHub/GitHub_12_11_19/SD_County_LowFlow/Flow Summary/Compiled Flow and Totals 2019/CAR-070-Flow and Totals.xlsx", 
                                      #sheet = "CAR-070-CTRSC Flow Data")

#read in survey data
surveys <- read_excel("GitHub/SD_County_LowFlow/0 - Ancillary files/Survey Schedules.xlsx", 
                               sheet = "Survey Periods")
surveys=as.data.frame(surveys)
head(surveys)


#Flow.totals= 
#read in flow data
flow.files=list.files("//sdg1-fs1/SDShare/Projects-South/Environmental - Schaedler/5025-19-W006 CoSDWQ TO6 Low Flow Monitoring/DATA/GitHub/GitHub_12_11_19/SD_County_LowFlow/Flow Summary/Compiled Flow and Totals 2019/")#,pattern="csv")

#### update with site id here ###
site_id= "CAR-072"

flow.file=paste(site_id,"-Flow and Totals.xlsx",sep = "")

flow.data <- read_excel(paste("//sdg1-fs1/SDShare/Projects-South/Environmental - Schaedler/5025-19-W006 CoSDWQ TO6 Low Flow Monitoring/DATA/GitHub/GitHub_12_11_19/SD_County_LowFlow/Flow Summary/Compiled Flow and Totals 2019/",flow.file,sep=""),
                        sheet =paste(site_id,"-CTRSC Flow Data",sep=""))# "CAR-070-CTRSC Flow Data")
flow.df= as.data.frame(flow.data)
head(flow.df)
flow.df=plyr::rename(flow.df,c("...1"="date.time"))
head(flow.df)




all.flow<- plot_ly(flow.df) %>%
  add_trace(x = ~date.time, y = ~`Flow compound weir stormflow clipped (gpm)`,name = 'Flow (gpm)',type = 'scatter',mode = 'lines')%>%
  layout(title= paste(site_id,"Flow",sep = " "),xaxis= list(title="date"), yaxis= list(title="Flow (gpm)"))


all.flow

plot(flow.df$date.time,flow.df$`Flow compound weir stormflow clipped (gpm)`,type = "l",xlab = "Date",ylab = "Flow (gpm)")

class(flow.df$date.time)

Mar=as.POSIXct(c("2019-03-01", "2019-03-30"))
May=as.POSIXct(c("2019-05-01", "2019-05-30"))
Jun=as.POSIXct(c("2019-06-01", "2019-06-30"))
July=as.POSIXct(c("2019-07-01", "2019-07-30"))

plot(flow.df$date.time,flow.df$`Flow compound weir stormflow clipped (gpm)`,type = "l",xlab = "Date",ylab = "Flow (gpm)",xlim = May)

#grab the observations for that site
site.obs.sub=surveys[grep(site_id,surveys$Outfall),]
May.obs=site.obs.sub[grep("May",site.obs.sub$`Month (Initial Survey)`),]
#May.obs.range=(c(as.POSIXct(May.obs$`Initial Survey Period Start Date/Time`,tz="PDT"),as.POSIXct(May.obs$`Initial Survey Period End Date/Time`,tz="UTC")))
#May.obs.range=as.POSIXct(May.obs.range,tz="PDT")
may.1=as.character(May.obs$`Initial Survey Period Start Date/Time`)
may.2=as.character(May.obs$`Initial Survey Period End Date/Time`)
May.obs.range=c(as.POSIXct(may.1),as.POSIXct(may.2))



Jun.obs=site.obs.sub[grep("June",site.obs.sub$`Month (Initial Survey)`),]
#Jun.obs.range=as.POSIXct(c(Jun.obs$`Initial Survey Period Start Date/Time`,Jun.obs$`Initial Survey Period End Date/Time`))
Jun.1=as.character(Jun.obs$`Initial Survey Period Start Date/Time`)
Jun.2=as.character(Jun.obs$`Initial Survey Period End Date/Time`)
Jun.obs.range=c(as.POSIXct(Jun.1),as.POSIXct(Jun.2))




July.obs=site.obs.sub[grep("July",site.obs.sub$`Month (Initial Survey)`),]
#July.obs.range=as.POSIXct(c(July.obs$`Initial Survey Period Start Date/Time`,July.obs$`Initial Survey Period End Date/Time`))
July.1=as.character(July.obs$`Initial Survey Period Start Date/Time`)
July.2=as.character(July.obs$`Initial Survey Period End Date/Time`)
July.obs.range=c(as.POSIXct(July.1),as.POSIXct(July.2))




May.flow.total= "90,176"
May.flow.total=subset(flow.df, date.time> as.POSIXct("2019-05-01 00:00:00",tz="America/Los_Angeles") & date.time < as.POSIXct("2019-05-31 00:23:59"),tz="America/Los_Angeles")
tail(May.flow.total)
May.flow.total <- flow.df %>%
  filter(date.time >= as.Date('2019-05-01') & date.time < as.Date('2019-06-1'))
#tail(May.flow.total)
#May.flow.total= filter(flow.df, filter(date.time>"2019-05-01" & date.time<"2019-05-31"))
Jun.flow.total= "88,863"

  
par(mfrow = c(1,1))
plot((flow.df$date.time),flow.df$`Flow compound weir stormflow clipped (gpm)`,type = "l",xlab = "Date",ylab = "Flow (gpm)",xlim = May, ylim = c(0,20),col="blue" ,xaxt="n")
axis.POSIXct(1,flow.df$date.time)
plot(flow.df$date.time,flow.df$`Flow compound weir stormflow clipped (gpm)`,type = "l",xlab = "Date",ylab = "Flow (gpm)",xlim = May.obs.range, ylim = c(0,20),col="blue" )

class(flow.df$date.time)
######## May #####

May.flow<- plot_ly(flow.df) %>%
  add_trace(x = ~date.time, y = ~`Flow compound weir stormflow clipped (gpm)`,name = 'Flow (gpm)',type = 'scatter',mode = 'lines',line=list(color='rgb(5, 71, 176)'))%>%
  layout(title= paste(site_id,"Flow",sep = " "),xaxis= list(range=May,title="date"), yaxis= list(range=c(0,25),title="Flow (gpm)"))%>%
  add_annotations(
    x= .8,
    y= .9,
    xref = "paper",
    yref = "paper",
    text = paste("Monthly Flow (gal):",May.flow.total),
    showarrow = F
  )

May.flow


May.obs.flow<- plot_ly(flow.df) %>%
  add_trace(x = ~date.time, y = ~`Flow compound weir stormflow clipped (gpm)`,name = 'Flow (gpm)',type = 'scatter',mode = 'lines',line=list(color='rgb(5, 71, 176)'))%>%
  layout(title= paste(site_id,"Flow",sep = " "),xaxis= list(range=May.obs.range,title="date"), yaxis= list(range=c(0,20),title="Flow (gpm)"),showlegend = FALSE)

May.obs.flow

########  June ######
Jun.flow<- plot_ly(flow.df) %>%
  add_trace(x = ~date.time, y = ~`Flow compound weir stormflow clipped (gpm)`,name = 'Flow (gpm)',type = 'scatter',mode = 'lines',line=list(color='rgb(5, 71, 176)'))%>%
  layout(title= paste(site_id,"Flow",sep = " "),xaxis= list(range=Jun,title="date"), yaxis= list(range=c(0,25),title="Flow (gpm)"),showlegend = FALSE)%>%
  add_annotations(
    x= .8,
    y= .9,
    xref = "paper",
    yref = "paper",
    text = paste("Monthly Flow (gal):",Jun.flow.total),
    showarrow = F
  )

Jun.flow


Jun.obs.flow<- plot_ly(flow.df) %>%
  add_trace(x = ~date.time, y = ~`Flow compound weir stormflow clipped (gpm)`,name = 'Flow (gpm)',type = 'scatter',mode = 'lines',line=list(color='rgb(5, 71, 176)'))%>%
  layout(title= paste(site_id,"Flow",sep = " "),xaxis= list(range=Jun.obs.range,title="date"), yaxis= list(range=c(0,20),title="Flow (gpm)"),showlegend = FALSE) 

Jun.obs.flow




July.obs.flow<- plot_ly(flow.df) %>%
  add_trace(x = ~date.time, y = ~`Flow compound weir stormflow clipped (gpm)`,name = 'Flow (gpm)',type = 'scatter',mode = 'lines',line=list(color='rgb(5, 71, 176)'))%>%
  layout(title= paste(site_id,"Flow",sep = " "),xaxis= list(range=July.obs.range,title="date"), yaxis= list(range=c(0,20),title="Flow (gpm)"),showlegend = FALSE) 

July.obs.flow


same.months <-subplot(nrows=2,margin= 0.05,titleY = TRUE, titleX = TRUE, May.flow,May.obs.flow,Jun.flow,Jun.obs.flow)
same.months

next.month<-subplot(nrows=2,margin= 0.05,titleY = TRUE, titleX = TRUE, May.flow,Jun.obs.flow,Jun.flow,July.obs.flow)
next.month

#export(next.month, file = "flow_reduction_plot.png")

#plotly_IMAGE(next.month, width = 500, height = 500, format = "png", scale = 2,
             out_file = "~/desktop/test.png")
