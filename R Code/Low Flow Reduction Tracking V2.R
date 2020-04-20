################## packages ################
library(plotly)
library(readxl)
library(plyr)
library(zoo)
library(dplyr)
library(lubridate)


######## Clear all #####
rm(list = ls())



###################################
###### Section 1: Read in Data ####
###################################

#read in survey data
surveys <- read_excel("GitHub/SD_County_LowFlow/0 - Ancillary files/Survey Schedules.xlsx", 
                      sheet = "Survey Periods")
surveys=as.data.frame(surveys)


observations <- read_excel("GitHub/SD_County_LowFlow/0 - Ancillary files/Schedule and Observations.xlsx", 
                               sheet = "Outfall_and_HSA_Survey_Tracking")
observations=as.data.frame(observations)


head(observations)

##### Will have to figure out if we want to read this in or not###
#Flow.totals= 



###### #read in flow data #####
flow.files=list.files("//sdg1-fs1/SDShare/Projects-South/Environmental - Schaedler/5025-19-W006 CoSDWQ TO6 Low Flow Monitoring/DATA/GitHub/GitHub_12_11_19/SD_County_LowFlow/Flow Summary/Compiled Flow and Totals 2019/")#,pattern="csv")

#################################
####### Update Site ID Here #####
#################################
site_id= "CAR-072"

#grab name of file you want
flow.file=paste(site_id,"-Flow and Totals.xlsx",sep = "")

#read the file in
flow.data <- read_excel(paste("//sdg1-fs1/SDShare/Projects-South/Environmental - Schaedler/5025-19-W006 CoSDWQ TO6 Low Flow Monitoring/DATA/GitHub/GitHub_12_11_19/SD_County_LowFlow/Flow Summary/Compiled Flow and Totals 2019/",flow.file,sep=""),
                        sheet =paste(site_id,"-CTRSC Flow Data",sep=""))
#convert to data frame
flow.df= as.data.frame(flow.data)

#rename first column to date.time because it gets weird 
flow.df=plyr::rename(flow.df,c("...1"="date.time"))


#############################################
###### Section 2: Make Individual Plots #####
#############################################

####### Tell R what the months are #########
May=as.POSIXct(c("2019-05-01", "2019-05-31"))
Jun=as.POSIXct(c("2019-06-01", "2019-06-30"))
July=as.POSIXct(c("2019-07-01", "2019-07-31"))
Aug=as.POSIXct(c("2019-08-01", "2019-08-31"))
Sep=as.POSIXct(c("2019-09-01", "2019-09-30"))

#####merge the flow data with the fail observation data######
class(observations$`Time of Observation 24-hr Time`)
observations$date.time=lubridate::round_date(observations$date.time, "5 minutes") 

#full.flow.and.cal=merge(compiled.flow.data,compiled.site.data[,c(2:6,24)],all.x = TRUE,all.y = TRUE,by.x ="X", by.y="date.time")
full.flow.and.obs=merge(flow.df,observations[,c(4,7:8)],all.x = FALSE,all.y = TRUE, by="date.time")


## find the max level to use for plotting purposes ###
max.level=max(flow.df$`Flow compound weir stormflow clipped (gpm)`,na.rm=T)


#plot the whole monitoring season
all.flow<- plot_ly(flow.df) %>%
  add_trace(x = ~date.time, y = ~`Flow compound weir stormflow clipped (gpm)`,name = 'Flow (gpm)',type = 'scatter',mode = 'lines')%>%
  add_trace(x = full.flow.and.obs$date.time, y = full.flow.and.obs$`Flow compound weir stormflow clipped (gpm)`,name = 'observation',mode = 'markers',marker = list(size=6,opacity = 0.85,symbol= "circle-x",color="red"),type = 'scatter' )%>%
  layout(title= paste(site_id,"Flow",sep = " "),xaxis= list(title="date"), yaxis= list(title="Flow (gpm)", range=c(0,max.level)))
all.flow

# do it in base plotting
plot(flow.df$date.time,flow.df$`Flow compound weir stormflow clipped (gpm)`,type = "l",xlab = "Date",ylab = "Flow (gpm)")



#plot may with base plotting. This doesn't do dates well
plot(flow.df$date.time,flow.df$`Flow compound weir stormflow clipped (gpm)`,type = "l",xlab = "Date",ylab = "Flow (gpm)",xlim = May)


#tell R how many seconds are in days
d7.days = 604800
d14.days=d7.days*2
d21.days=d14.days*4

#grab the May observations for that site
site.obs.sub=surveys[grep(site_id,surveys$Outfall),]
May.obs=site.obs.sub[grep("May",site.obs.sub$`Month (Initial Survey)`),]
may.1=as.character(May.obs$`Initial Survey Period Start Date/Time`)
may.2=as.character(May.obs$`Initial Survey Period End Date/Time`)
May.obs.range=c(as.POSIXct(may.1),as.POSIXct(may.2))



#May observation repeats
may.obs.start=as.POSIXct(may.1)
may.obs.end=as.POSIXct(may.2)

  may.start.obs <- c(may.obs.start + d7.days, may.obs.start + d14.days,may.obs.start + d21.days,
               may.obs.start - d7.days, may.obs.start - d14.days,may.obs.start - d21.days)
  may.obs.repeats <- as.data.frame( c(may.obs.start,may.start.obs))

  may.end.obs <- c(may.obs.end + d7.days, may.obs.end + d14.days,may.obs.end + d21.days,
                may.obs.end - d7.days, may.obs.end - d14.days,may.obs.end - d21.days)

  may.obs.repeats$end.obs <- c(may.obs.end,may.end.obs)
  
  may.obs.repeats=plyr::rename(may.obs.repeats,c("c(may.obs.start, may.start.obs)"="obs.start"))
  


##grab the June observations 
jun.obs=site.obs.sub[grep("June",site.obs.sub$`Month (Initial Survey)`),]
jun.1=as.character(jun.obs$`Initial Survey Period Start Date/Time`)
jun.2=as.character(jun.obs$`Initial Survey Period End Date/Time`)
jun.obs.range=c(as.POSIXct(jun.1),as.POSIXct(jun.2))


#June observation repeats
jun.obs.start=as.POSIXct(jun.1)
jun.obs.end=as.POSIXct(jun.2)

jun.start.obs <- c(jun.obs.start + d7.days, jun.obs.start + d14.days,jun.obs.start + d21.days,
                   jun.obs.start - d7.days, jun.obs.start - d14.days,jun.obs.start - d21.days)
jun.obs.repeats <- as.data.frame( c(jun.obs.start,jun.start.obs))

jun.end.obs <- c(jun.obs.end + d7.days, jun.obs.end + d14.days,jun.obs.end + d21.days,
                 jun.obs.end - d7.days, jun.obs.end - d14.days,jun.obs.end - d21.days)

jun.obs.repeats$end.obs <- c(jun.obs.end,jun.end.obs)

jun.obs.repeats=plyr::rename(jun.obs.repeats,c("c(jun.obs.start, jun.start.obs)"="obs.start"))


## grab the July observations 
July.obs=site.obs.sub[grep("July",site.obs.sub$`Month (Initial Survey)`),]
July.1=as.character(July.obs$`Initial Survey Period Start Date/Time`)
July.2=as.character(July.obs$`Initial Survey Period End Date/Time`)
July.obs.range=c(as.POSIXct(July.1),as.POSIXct(July.2))


#July observation repeats
July.obs.start=as.POSIXct(July.1)
July.obs.end=as.POSIXct(July.2)

July.start.obs <- c(July.obs.start + d7.days, July.obs.start + d14.days,July.obs.start + d21.days,
                   July.obs.start - d7.days, July.obs.start - d14.days,July.obs.start - d21.days)
July.obs.repeats <- as.data.frame( c(July.obs.start,July.start.obs))

July.end.obs <- c(July.obs.end + d7.days, July.obs.end + d14.days,July.obs.end + d21.days,
                 July.obs.end - d7.days, July.obs.end - d14.days,July.obs.end - d21.days)

July.obs.repeats$end.obs <- c(July.obs.end,July.end.obs)

July.obs.repeats=plyr::rename(July.obs.repeats,c("c(July.obs.start, July.start.obs)"="obs.start"))



## grab the August observations 
aug.obs=site.obs.sub[grep("August",site.obs.sub$`Month (Initial Survey)`),]
aug.1=as.character(aug.obs$`Initial Survey Period Start Date/Time`)
aug.2=as.character(aug.obs$`Initial Survey Period End Date/Time`)
aug.obs.range=c(as.POSIXct(aug.1),as.POSIXct(aug.2))


#August observation repeats
aug.obs.start=as.POSIXct(aug.1)
aug.obs.end=as.POSIXct(aug.2)

aug.start.obs <- c(aug.obs.start + d7.days, aug.obs.start + d14.days,aug.obs.start + d21.days,
                    aug.obs.start - d7.days, aug.obs.start - d14.days,aug.obs.start - d21.days)
aug.obs.repeats <- as.data.frame( c(aug.obs.start,aug.start.obs))

aug.end.obs <- c(aug.obs.end + d7.days, aug.obs.end + d14.days,aug.obs.end + d21.days,
                  aug.obs.end - d7.days, aug.obs.end - d14.days,aug.obs.end - d21.days)

aug.obs.repeats$end.obs <- c(aug.obs.end,aug.end.obs)

aug.obs.repeats=plyr::rename(aug.obs.repeats,c("c(aug.obs.start, aug.start.obs)"="obs.start"))


## grab the September observations 
sep.obs=site.obs.sub[grep("September",site.obs.sub$`Month (Initial Survey)`),]
sep.1=as.character(sep.obs$`Initial Survey Period Start Date/Time`)
sep.2=as.character(sep.obs$`Initial Survey Period End Date/Time`)
sep.obs.range=c(as.POSIXct(sep.1),as.POSIXct(sep.2))


#August observation repeats
sep.obs.start=as.POSIXct(sep.1)
sep.obs.end=as.POSIXct(sep.2)

sep.start.obs <- c(sep.obs.start + d7.days, sep.obs.start + d14.days,sep.obs.start + d21.days,
                   sep.obs.start - d7.days, sep.obs.start - d14.days,sep.obs.start - d21.days)
sep.obs.repeats <- as.data.frame( c(sep.obs.start,sep.start.obs))

sep.end.obs <- c(sep.obs.end + d7.days, sep.obs.end + d14.days,sep.obs.end + d21.days,
                 sep.obs.end - d7.days, sep.obs.end - d14.days,sep.obs.end - d21.days)

sep.obs.repeats$end.obs <- c(sep.obs.end,sep.end.obs)

sep.obs.repeats=plyr::rename(sep.obs.repeats,c("c(sep.obs.start, sep.start.obs)"="obs.start"))



### manual flow total for now
May.flow.total= "90,176"

#May.flow.total=subset(flow.df, date.time> as.POSIXct("2019-05-01 00:00:00",tz="America/Los_Angeles") & date.time < as.POSIXct("2019-05-31 00:23:59"),tz="America/Los_Angeles")
#tail(May.flow.total)
#May.flow.total <- flow.df %>%
# filter(date.time >= as.Date('2019-05-01') & date.time < as.Date('2019-06-1'))
#tail(May.flow.total)
#May.flow.total= filter(flow.df, filter(date.time>"2019-05-01" & date.time<"2019-05-31"))

#manual june flow total for now
May.flow.total= "90,176"
jun.flow.total= "88,863"
jul.flow.total= "-"
aug.flow.total= "-"
sep.flow.total= "-"




######## Plots for  May #####
May.flow<- plot_ly(flow.df) %>%
  add_trace(x = ~date.time, y = ~`Flow compound weir stormflow clipped (gpm)`,name = 'Flow (gpm)',
            type = 'scatter',mode = 'lines',line=list(color='rgb(5, 71, 176)'))%>%
  layout(title= paste(site_id,sep = " "),
         xaxis= list(range=May,autotick = F, dtick = 86400000,tickfont = list(size = 8),
                     type='date',
                     tickformat = "%a <br>%e"), 
         yaxis= list(title="Flow (gpm)",range=c(0,35)),
         shapes = list(
           list(type = "rect",
                fillcolor = "#9c9c9c", line = list(color = "#525252"), opacity = 0.3,
                x0 = may.obs.repeats$obs.start[1], x1 = may.obs.repeats$end.obs[1], xref = "x",
                y0 = 0, y1 = 1, yref = "paper"),
           list(type = "rect",
                fillcolor = "#9c9c9c", line = list(color = "#525252"), opacity = 0.3,
                x0 = may.obs.repeats$obs.start[2], x1 = may.obs.repeats$end.obs[2], xref = "x",
                y0 = 0, y1 = 1, yref = "paper"),
           list(type = "rect",
                fillcolor = "#9c9c9c", line = list(color = "#525252"), opacity = 0.3,
                x0 = may.obs.repeats$obs.start[3], x1 = may.obs.repeats$end.obs[3], xref = "x",
                y0 = 0, y1 = 1, yref = "paper"),
           list(type = "rect",
                fillcolor = "#9c9c9c", line = list(color = "#525252"), opacity = 0.3,
                x0 = may.obs.repeats$obs.start[4], x1 = may.obs.repeats$end.obs[4], xref = "x",
                y0 = 0, y1 = 1, yref = "paper"),
           list(type = "rect",
                fillcolor = "#9c9c9c", line = list(color = "#525252"), opacity = 0.3,
                x0 = may.obs.repeats$obs.start[5], x1 = may.obs.repeats$end.obs[5], xref = "x",
                y0 = 0, y1 = 1, yref = "paper"),
           list(type = "rect",
                fillcolor = "#9c9c9c", line = list(color = "#525252"), opacity = 0.3,
                x0 = may.obs.repeats$obs.start[6], x1 = may.obs.repeats$end.obs[6], xref = "x",
                y0 = 0, y1 = 1, yref = "paper"),
           list(type = "rect",
                fillcolor = "#9c9c9c", line = list(color = "#525252"), opacity = 0.3,
                x0 = may.obs.repeats$obs.start[7], x1 = may.obs.repeats$end.obs[7], xref = "x",
                y0 = 0, y1 = 1, yref = "paper")
           )
         )%>%
  add_annotations(
    x= .8,
    y= .9,
    xref = "paper",
    yref = "paper",
    text = paste("Monthly Flow (gal):",May.flow.total),
    showarrow = F
  ) %>%
  add_annotations(
    text = paste(site_id,"May Flow Data",sep = " "), x = 0,
    y = 1,yref = "paper",xref = "paper",xanchor = "middle",yanchor = "top",showarrow = FALSE,font = list(size = 20)
  )

May.flow


May.obs.flow<- plot_ly(flow.df) %>%
  add_trace(x = ~date.time, y = ~`Flow compound weir stormflow clipped (gpm)`,
            name = 'Flow (gpm)',type = 'scatter',mode = 'lines',line=list(color='rgb(5, 71, 176)'))%>%
  add_trace(x = full.flow.and.obs$date.time, y = full.flow.and.obs$`Flow compound weir stormflow clipped (gpm)`,name = 'observation',mode = 'markers',marker = list(size=6,opacity = 0.85,symbol= "circle-x",color="red"),type = 'scatter' )%>%
  layout(
    xaxis= list(range=May.obs.range,title="date"), 
    yaxis= list(range=c(0,20),title="Flow (gpm)"),showlegend = FALSE
  ) %>%
  add_annotations(
    text = paste(site_id,"May Observation",sep = " "),
    x = 0.5, y = 1,
    yref = "paper",xref = "paper",xanchor = "middle",yanchor = "top",
    showarrow = FALSE,font = list(size = 10)
  )
May.obs.flow

########  June ######
jun.flow<- plot_ly(flow.df) %>%
  add_trace(x = ~date.time, y = ~`Flow compound weir stormflow clipped (gpm)`,name = 'Flow (gpm)',
            type = 'scatter',mode = 'lines',line=list(color='rgb(5, 71, 176)'))%>%
  layout(title= paste(site_id,sep = " "),
         xaxis= list(range=Jun,autotick = F, dtick = 86400000,tickfont = list(size = 8),
                     type='date',
                     tickformat = "%a <br>%e"), 
         yaxis= list(title="Flow (gpm)",range=c(0,35)),
         shapes = list(
           list(type = "rect",
                fillcolor = "#9c9c9c", line = list(color = "#525252"), opacity = 0.3,
                x0 = jun.obs.repeats$obs.start[1], x1 = jun.obs.repeats$end.obs[1], xref = "x",
                y0 = 0, y1 = 1, yref = "paper"),
           list(type = "rect",
                fillcolor = "#9c9c9c", line = list(color = "#525252"), opacity = 0.3,
                x0 = jun.obs.repeats$obs.start[2], x1 = jun.obs.repeats$end.obs[2], xref = "x",
                y0 = 0, y1 = 1, yref = "paper"),
           list(type = "rect",
                fillcolor = "#9c9c9c", line = list(color = "#525252"), opacity = 0.3,
                x0 = jun.obs.repeats$obs.start[3], x1 = jun.obs.repeats$end.obs[3], xref = "x",
                y0 = 0, y1 = 1, yref = "paper"),
           list(type = "rect",
                fillcolor = "#9c9c9c", line = list(color = "#525252"), opacity = 0.3,
                x0 = jun.obs.repeats$obs.start[4], x1 = jun.obs.repeats$end.obs[4], xref = "x",
                y0 = 0, y1 = 1, yref = "paper"),
           list(type = "rect",
                fillcolor = "#9c9c9c", line = list(color = "#525252"), opacity = 0.3,
                x0 = jun.obs.repeats$obs.start[5], x1 = jun.obs.repeats$end.obs[5], xref = "x",
                y0 = 0, y1 = 1, yref = "paper"),
           list(type = "rect",
                fillcolor = "#9c9c9c", line = list(color = "#525252"), opacity = 0.3,
                x0 = jun.obs.repeats$obs.start[6], x1 = jun.obs.repeats$end.obs[6], xref = "x",
                y0 = 0, y1 = 1, yref = "paper"),
           list(type = "rect",
                fillcolor = "#9c9c9c", line = list(color = "#525252"), opacity = 0.3,
                x0 = jun.obs.repeats$obs.start[7], x1 = jun.obs.repeats$end.obs[7], xref = "x",
                y0 = 0, y1 = 1, yref = "paper")
         )
  )%>%
  add_annotations(
    x= .8,
    y= .9,
    xref = "paper",
    yref = "paper",
    text = paste("Monthly Flow (gal):",jun.flow.total),
    showarrow = F
  ) %>%
  add_annotations(
    text = paste(site_id,"June Flow Data",sep = " "), x = 0,
    y = 1,yref = "paper",xref = "paper",xanchor = "middle",yanchor = "top",showarrow = FALSE,font = list(size = 20)
  )

jun.flow


Jun.obs.flow<- plot_ly(flow.df) %>%
  add_trace(x = ~date.time, y = ~`Flow compound weir stormflow clipped (gpm)`,
            name = 'Flow (gpm)',type = 'scatter',mode = 'lines',line=list(color='rgb(5, 71, 176)'))%>%
  add_trace(x = full.flow.and.obs$date.time, y = full.flow.and.obs$`Flow compound weir stormflow clipped (gpm)`,name = 'observation',mode = 'markers',marker = list(size=6,opacity = 0.85,symbol= "circle-x",color="red"),type = 'scatter' )%>%
  layout(
    xaxis= list(range=jun.obs.range,title="date"), 
    yaxis= list(range=c(0,20),title="Flow (gpm)"),showlegend = FALSE
  ) %>%
  add_annotations(
    text = paste(site_id,"June Observation",sep = " "),
    x = 0.5, y = 1,
    yref = "paper",xref = "paper",xanchor = "middle",yanchor = "top",
    showarrow = FALSE,font = list(size = 10)
  )

#Jun.obs.flow


### July
July.flow<- plot_ly(flow.df) %>%
  add_trace(x = ~date.time, y = ~`Flow compound weir stormflow clipped (gpm)`,name = 'Flow (gpm)',
            type = 'scatter',mode = 'lines',line=list(color='rgb(5, 71, 176)'))%>%
  layout(title= paste(site_id,sep = " "),
         xaxis= list(range=July,autotick = F, dtick = 86400000,tickfont = list(size = 8),
                     type='date',
                     tickformat = "%a <br>%e"), 
         yaxis= list(title="Flow (gpm)",range=c(0,35)),
         shapes = list(
           list(type = "rect",
                fillcolor = "#9c9c9c", line = list(color = "#525252"), opacity = 0.3,
                x0 = July.obs.repeats$obs.start[1], x1 = July.obs.repeats$end.obs[1], xref = "x",
                y0 = 0, y1 = 1, yref = "paper"),
           list(type = "rect",
                fillcolor = "#9c9c9c", line = list(color = "#525252"), opacity = 0.3,
                x0 = July.obs.repeats$obs.start[2], x1 = July.obs.repeats$end.obs[2], xref = "x",
                y0 = 0, y1 = 1, yref = "paper"),
           list(type = "rect",
                fillcolor = "#9c9c9c", line = list(color = "#525252"), opacity = 0.3,
                x0 = July.obs.repeats$obs.start[3], x1 = July.obs.repeats$end.obs[3], xref = "x",
                y0 = 0, y1 = 1, yref = "paper"),
           list(type = "rect",
                fillcolor = "#9c9c9c", line = list(color = "#525252"), opacity = 0.3,
                x0 = July.obs.repeats$obs.start[4], x1 = July.obs.repeats$end.obs[4], xref = "x",
                y0 = 0, y1 = 1, yref = "paper"),
           list(type = "rect",
                fillcolor = "#9c9c9c", line = list(color = "#525252"), opacity = 0.3,
                x0 = July.obs.repeats$obs.start[5], x1 = July.obs.repeats$end.obs[5], xref = "x",
                y0 = 0, y1 = 1, yref = "paper"),
           list(type = "rect",
                fillcolor = "#9c9c9c", line = list(color = "#525252"), opacity = 0.3,
                x0 = July.obs.repeats$obs.start[6], x1 = July.obs.repeats$end.obs[6], xref = "x",
                y0 = 0, y1 = 1, yref = "paper"),
           list(type = "rect",
                fillcolor = "#9c9c9c", line = list(color = "#525252"), opacity = 0.3,
                x0 = July.obs.repeats$obs.start[7], x1 = July.obs.repeats$end.obs[7], xref = "x",
                y0 = 0, y1 = 1, yref = "paper")
         )
  )%>%
  add_annotations(
    x= .8,
    y= .9,
    xref = "paper",
    yref = "paper",
    text = paste("Monthly Flow (gal):",jul.flow.total),
    showarrow = F
  ) %>%
  add_annotations(
    text = paste(site_id,"July Flow Data",sep = " "), x = 0,
    y = 1,yref = "paper",xref = "paper",xanchor = "middle",yanchor = "top",showarrow = FALSE,font = list(size = 20)
  )

July.flow


July.obs.flow<- plot_ly(flow.df) %>%
  add_trace(x = ~date.time, y = ~`Flow compound weir stormflow clipped (gpm)`,name = 'Flow (gpm)',type = 'scatter',mode = 'lines',line=list(color='rgb(5, 71, 176)'))%>%
  add_trace(x = full.flow.and.obs$date.time, y = full.flow.and.obs$`Flow compound weir stormflow clipped (gpm)`,name = 'observation',mode = 'markers',marker = list(size=6,opacity = 0.85,symbol= "circle-x",color="red"),type = 'scatter' )%>%
  layout(
    xaxis= list(range=July.obs.range), 
    yaxis= list(range=c(0,20),title="Flow (gpm)"),showlegend = FALSE
  )  %>%
  add_annotations(
    text = paste(site_id,"July Observation",sep = " "), x = 0.8,
    y = 1,yref = "paper",xref = "paper",xanchor = "middle",yanchor = "top",showarrow = FALSE,font = list(size = 10)
  )

July.obs.flow


######### Plots for august
aug.flow<- plot_ly(flow.df) %>%
  add_trace(x = ~date.time, y = ~`Flow compound weir stormflow clipped (gpm)`,name = 'Flow (gpm)',
            type = 'scatter',mode = 'lines',line=list(color='rgb(5, 71, 176)'))%>%
  layout(title= paste(site_id,sep = " "),
         xaxis= list(range=Aug,autotick = F, dtick = 86400000,tickfont = list(size = 8),
                     type='date',
                     tickformat = "%a <br>%e"), 
         yaxis= list(title="Flow (gpm)",range=c(0,35)),
         shapes = list(
           list(type = "rect",
                fillcolor = "#9c9c9c", line = list(color = "#525252"), opacity = 0.3,
                x0 = aug.obs.repeats$obs.start[1], x1 = aug.obs.repeats$end.obs[1], xref = "x",
                y0 = 0, y1 = 1, yref = "paper"),
           list(type = "rect",
                fillcolor = "#9c9c9c", line = list(color = "#525252"), opacity = 0.3,
                x0 = aug.obs.repeats$obs.start[2], x1 = aug.obs.repeats$end.obs[2], xref = "x",
                y0 = 0, y1 = 1, yref = "paper"),
           list(type = "rect",
                fillcolor = "#9c9c9c", line = list(color = "#525252"), opacity = 0.3,
                x0 = aug.obs.repeats$obs.start[3], x1 = aug.obs.repeats$end.obs[3], xref = "x",
                y0 = 0, y1 = 1, yref = "paper"),
           list(type = "rect",
                fillcolor = "#9c9c9c", line = list(color = "#525252"), opacity = 0.3,
                x0 = aug.obs.repeats$obs.start[4], x1 = aug.obs.repeats$end.obs[4], xref = "x",
                y0 = 0, y1 = 1, yref = "paper"),
           list(type = "rect",
                fillcolor = "#9c9c9c", line = list(color = "#525252"), opacity = 0.3,
                x0 = aug.obs.repeats$obs.start[5], x1 = aug.obs.repeats$end.obs[5], xref = "x",
                y0 = 0, y1 = 1, yref = "paper"),
           list(type = "rect",
                fillcolor = "#9c9c9c", line = list(color = "#525252"), opacity = 0.3,
                x0 = aug.obs.repeats$obs.start[6], x1 = aug.obs.repeats$end.obs[6], xref = "x",
                y0 = 0, y1 = 1, yref = "paper"),
           list(type = "rect",
                fillcolor = "#9c9c9c", line = list(color = "#525252"), opacity = 0.3,
                x0 = aug.obs.repeats$obs.start[7], x1 = aug.obs.repeats$end.obs[7], xref = "x",
                y0 = 0, y1 = 1, yref = "paper")
         )
  )%>%
  add_annotations(
    x= .8,
    y= .9,
    xref = "paper",
    yref = "paper",
    text = paste("Monthly Flow (gal):",aug.flow.total),
    showarrow = F
  ) %>%
  add_annotations(
    text = paste(site_id,"August Flow Data",sep = " "), x = 0,
    y = 1,yref = "paper",xref = "paper",xanchor = "middle",yanchor = "top",showarrow = FALSE,font = list(size = 20)
  )

aug.flow


aug.obs.flow<- plot_ly(flow.df) %>%
  add_trace(x = ~date.time, y = ~`Flow compound weir stormflow clipped (gpm)`,
            name = 'Flow (gpm)',type = 'scatter',mode = 'lines',line=list(color='rgb(5, 71, 176)'))%>%
  add_trace(x = full.flow.and.obs$date.time, y = full.flow.and.obs$`Flow compound weir stormflow clipped (gpm)`,name = 'observation',mode = 'markers',marker = list(size=6,opacity = 0.85,symbol= "circle-x",color="red"),type = 'scatter' )%>%
  layout(
    xaxis= list(range=aug.obs.range,title="date"), 
    yaxis= list(range=c(0,20),title="Flow (gpm)"),showlegend = FALSE
  ) %>%
  add_annotations(
    text = paste(site_id,"August Observation",sep = " "),
    x = 0.5, y = 1,
    yref = "paper",xref = "paper",xanchor = "middle",yanchor = "top",
    showarrow = FALSE,font = list(size = 10)
  )
aug.obs.flow

############ Plots for september ###########
sep.flow<- plot_ly(flow.df) %>%
  add_trace(x = ~date.time, y = ~`Flow compound weir stormflow clipped (gpm)`,name = 'Flow (gpm)',
            type = 'scatter',mode = 'lines',line=list(color='rgb(5, 71, 176)'))%>%
  layout(title= paste(site_id,sep = " "),
         xaxis= list(range=Sep,autotick = F, dtick = 86400000,tickfont = list(size = 8),
                     type='date',
                     tickformat = "%a <br>%e"), 
         yaxis= list(title="Flow (gpm)",range=c(0,35)),
         shapes = list(
           list(type = "rect",
                fillcolor = "#9c9c9c", line = list(color = "#525252"), opacity = 0.3,
                x0 = sep.obs.repeats$obs.start[1], x1 = sep.obs.repeats$end.obs[1], xref = "x",
                y0 = 0, y1 = 1, yref = "paper"),
           list(type = "rect",
                fillcolor = "#9c9c9c", line = list(color = "#525252"), opacity = 0.3,
                x0 = sep.obs.repeats$obs.start[2], x1 = sep.obs.repeats$end.obs[2], xref = "x",
                y0 = 0, y1 = 1, yref = "paper"),
           list(type = "rect",
                fillcolor = "#9c9c9c", line = list(color = "#525252"), opacity = 0.3,
                x0 = sep.obs.repeats$obs.start[3], x1 = sep.obs.repeats$end.obs[3], xref = "x",
                y0 = 0, y1 = 1, yref = "paper"),
           list(type = "rect",
                fillcolor = "#9c9c9c", line = list(color = "#525252"), opacity = 0.3,
                x0 = sep.obs.repeats$obs.start[4], x1 = sep.obs.repeats$end.obs[4], xref = "x",
                y0 = 0, y1 = 1, yref = "paper"),
           list(type = "rect",
                fillcolor = "#9c9c9c", line = list(color = "#525252"), opacity = 0.3,
                x0 = sep.obs.repeats$obs.start[5], x1 = sep.obs.repeats$end.obs[5], xref = "x",
                y0 = 0, y1 = 1, yref = "paper"),
           list(type = "rect",
                fillcolor = "#9c9c9c", line = list(color = "#525252"), opacity = 0.3,
                x0 = sep.obs.repeats$obs.start[6], x1 = sep.obs.repeats$end.obs[6], xref = "x",
                y0 = 0, y1 = 1, yref = "paper"),
           list(type = "rect",
                fillcolor = "#9c9c9c", line = list(color = "#525252"), opacity = 0.3,
                x0 = sep.obs.repeats$obs.start[7], x1 = sep.obs.repeats$end.obs[7], xref = "x",
                y0 = 0, y1 = 1, yref = "paper")
         )
  )%>%
  add_annotations(
    x= .8,
    y= .9,
    xref = "paper",
    yref = "paper",
    text = paste("Monthly Flow (gal):",sep.flow.total),
    showarrow = F
  ) %>%
  add_annotations(
    text = paste(site_id,"September Flow Data",sep = " "), x = 0,
    y = 1,yref = "paper",xref = "paper",xanchor = "middle",yanchor = "top",showarrow = FALSE,font = list(size = 20)
  )

sep.flow


sep.obs.flow<- plot_ly(flow.df) %>%
  add_trace(x = ~date.time, y = ~`Flow compound weir stormflow clipped (gpm)`,
            name = 'Flow (gpm)',type = 'scatter',mode = 'lines',line=list(color='rgb(5, 71, 176)'))%>%
  add_trace(x = full.flow.and.obs$date.time, y = full.flow.and.obs$`Flow compound weir stormflow clipped (gpm)`,name = 'observation',mode = 'markers',marker = list(size=6,opacity = 0.85,symbol= "circle-x",color="red"),type = 'scatter' )%>%
  layout(
    xaxis= list(range=sep.obs.range,title="date"), 
    yaxis= list(range=c(0,20),title="Flow (gpm)"),showlegend = FALSE
  ) %>%
  add_annotations(
    text = paste(site_id,"Setember Observation",sep = " "),
    x = 0.5, y = 1,
    yref = "paper",xref = "paper",xanchor = "middle",yanchor = "top",
    showarrow = FALSE,font = list(size = 10)
  )
sep.obs.flow



######## Part 3. Start combining some plots dawg ####

#the monthly hydrographs
may.jun.flow <-subplot(shareY = TRUE,nrows = 2,May.flow,jun.flow)
jun.jul.flow <-subplot(shareY = TRUE,nrows = 2,jun.flow,July.flow)
jul.aug.flow <-subplot(shareY = TRUE,nrows = 2,July.flow,aug.flow)
aug.sep.flow <-subplot(shareY = TRUE,nrows = 2,aug.flow,sep.flow)


#the detail hydrographs with observation times
Jun.Jul.obs <-subplot(Jun.obs.flow,July.obs.flow,shareY = TRUE,margin= 0.05)#, shareX = TRUE)
Jul.Aug.obs <-subplot(July.obs.flow,aug.obs.flow,shareY = TRUE,margin= 0.05)#, shareX = TRUE)
Aug.Sep.obs <-subplot(aug.obs.flow,sep.obs.flow,shareY = TRUE,margin= 0.05)#, shareX = TRUE)


# Combine Monthly hydrographs with detail hydrographs
may.june.flow.obs<-subplot(nrows=1,margin= 0.05,titleY = TRUE, titleX = TRUE, may.jun.flow,Jun.Jul.obs)
june.july.flow.obs<-subplot(nrows=1,margin= 0.05,titleY = TRUE, titleX = TRUE, jun.jul.flow,Jul.Aug.obs)
july.aug.flow.obs<-subplot(nrows=1,margin= 0.05,titleY = TRUE, titleX = TRUE, jul.aug.flow,Aug.Sep.obs)

#aug.sep.flow.obs<-subplot(nrows=1,margin= 0.05,titleY = TRUE, titleX = TRUE, may.jun.flow,Jun.Jul.obs)

may.june.flow.obs



#working plotly export
export.dir="P:/Projects-South/Environmental - Schaedler/5025-19-I003 CoSD HSA and Outfall Surveys/7. Deliverables/Summary Report/Draft/DATA ANALYSIS/Flow Reduction Analysis/R Plots/"
#export.file=

setwd(export.dir)
getwd()

# May and June
orca(may.june.flow.obs,file =paste(site_id,"_May-Jun_Flow_reduction.png",sep = ""), width = 1700, height = 642)
# June and July
orca(june.july.flow.obs,file =paste(site_id,"_Jun-Jul_Flow_reduction.png",sep = ""), width = 1700, height = 642)
# July and August
orca(july.aug.flow.obs,file =paste(site_id,"_Jul-Aug_Flow_reduction.png",sep = ""), width = 1700, height = 642)




#export(may.june.flow.obs, file =paste(export.dir,"test_plo6t.png"))


htmlwidgets::saveWidget(may.june.flow.obs, file =paste(export.dir,"test_plot.html"))

plotly_IMAGE(may.june.flow.obs,  width = 800, height = 600, format = "png", scale = 1, out_file = paste(export.dir,"test_plot2.png"))

help(signup, package = 'plotly') 

