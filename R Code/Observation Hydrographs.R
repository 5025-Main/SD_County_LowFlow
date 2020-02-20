################## packages ################
library(plotly)
library(readxl)
library(plyr)
library(zoo)
library(dplyr)


######## Clear all #####
rm(list = ls())



###################################
###### Section 1: Read in Data ####
###################################

#read in survey data
surveys <- read_excel("GitHub/SD_County_LowFlow/0 - Ancillary files/Survey Schedules.xlsx", 
                               sheet = "Survey Periods")
surveys=as.data.frame(surveys)

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
Mar=as.POSIXct(c("2019-03-01", "2019-03-31"))
Mar=as.POSIXct(c("2019-04-01", "2019-04-30"))
May=as.POSIXct(c("2019-05-01", "2019-05-31"))
Jun=as.POSIXct(c("2019-06-01", "2019-06-30"))
July=as.POSIXct(c("2019-07-01", "2019-07-31"))
Aug=as.POSIXct(c("2019-08-01", "2019-08-31"))
Sep=as.POSIXct(c("2019-09-01", "2019-09-30"))

## find the max level to use for plotting purposes ###
max.level=max(flow.df$`Flow compound weir stormflow clipped (gpm)`,na.rm=T)


#plot the whole monitoring season
all.flow<- plot_ly(flow.df) %>%
  add_trace(x = ~date.time, y = ~`Flow compound weir stormflow clipped (gpm)`,name = 'Flow (gpm)',type = 'scatter',mode = 'lines')%>%
  layout(title= paste(site_id,"Flow",sep = " "),xaxis= list(title="date"), yaxis= list(title="Flow (gpm)", range=c(0,max.level)))
all.flow

# do it in base plotting
plot(flow.df$date.time,flow.df$`Flow compound weir stormflow clipped (gpm)`,type = "l",xlab = "Date",ylab = "Flow (gpm)")



#plot may with base plotting. This doesn't do dates well
plot(flow.df$date.time,flow.df$`Flow compound weir stormflow clipped (gpm)`,type = "l",xlab = "Date",ylab = "Flow (gpm)",xlim = May)

#grab the May observations for that site
site.obs.sub=surveys[grep(site_id,surveys$Outfall),]
May.obs=site.obs.sub[grep("May",site.obs.sub$`Month (Initial Survey)`),]
may.1=as.character(May.obs$`Initial Survey Period Start Date/Time`)
may.2=as.character(May.obs$`Initial Survey Period End Date/Time`)
May.obs.range=c(as.POSIXct(may.1),as.POSIXct(may.2))


##grab the June observations 
Jun.obs=site.obs.sub[grep("June",site.obs.sub$`Month (Initial Survey)`),]
Jun.1=as.character(Jun.obs$`Initial Survey Period Start Date/Time`)
Jun.2=as.character(Jun.obs$`Initial Survey Period End Date/Time`)
Jun.obs.range=c(as.POSIXct(Jun.1),as.POSIXct(Jun.2))

## grab the July observations 
July.obs=site.obs.sub[grep("July",site.obs.sub$`Month (Initial Survey)`),]
July.1=as.character(July.obs$`Initial Survey Period Start Date/Time`)
July.2=as.character(July.obs$`Initial Survey Period End Date/Time`)
July.obs.range=c(as.POSIXct(July.1),as.POSIXct(July.2))



### manual flow total for now
May.flow.total= "90,176"

#May.flow.total=subset(flow.df, date.time> as.POSIXct("2019-05-01 00:00:00",tz="America/Los_Angeles") & date.time < as.POSIXct("2019-05-31 00:23:59"),tz="America/Los_Angeles")
#tail(May.flow.total)
#May.flow.total <- flow.df %>%
 # filter(date.time >= as.Date('2019-05-01') & date.time < as.Date('2019-06-1'))
#tail(May.flow.total)
#May.flow.total= filter(flow.df, filter(date.time>"2019-05-01" & date.time<"2019-05-31"))

#manual june flow total for now
Jun.flow.total= "88,863"

  


######## Plots for  May #####

May.flow<- plot_ly(flow.df) %>%
  add_trace(x = ~date.time, y = ~`Flow compound weir stormflow clipped (gpm)`,name = 'Flow (gpm)',
            type = 'scatter',mode = 'lines',line=list(color='rgb(5, 71, 176)'))%>%
  layout(title= paste(site_id,"Flow",sep = " "),
         xaxis= list(range=May,autotick = F, dtick = 86400000,tickfont = list(size = 8),
                     type='date',
                     tickformat = "%a <br>%e"), 
         yaxis= list(title="Flow (gpm)"))%>%
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
  add_trace(x = ~date.time, y = ~`Flow compound weir stormflow clipped (gpm)`,
            name = 'Flow (gpm)',type = 'scatter',mode = 'lines',line=list(color='rgb(5, 71, 176)'))%>%
  layout(title= paste(site_id,"Flow",sep = " "),
         xaxis= list(range=May.obs.range,title="date"), 
         yaxis= list(range=c(0,20),title="Flow (gpm)"),showlegend = FALSE)

May.obs.flow


########  June ######
Jun.flow<- plot_ly(flow.df) %>%
  add_trace(x = ~date.time, y = ~`Flow compound weir stormflow clipped (gpm)`,
            name = 'Flow (gpm)',type = 'scatter',mode = 'lines',line=list(color='rgb(5, 71, 176)'))%>%
  layout(xaxis= list(range=May,autotick = F, dtick = 86400000,tickfont = list(size = 8),
                     type='date',
                     tickformat = "%a <br>%e"),  
        yaxis= list(title="Flow (gpm)"),showlegend = FALSE)%>%
  add_annotations(
                  x= .8, y= .9,
                  xref = "paper",yref = "paper",
                  text = paste("Monthly Flow (gal):",Jun.flow.total),
                  showarrow = F
  )

Jun.flow


Jun.obs.flow<- plot_ly(flow.df) %>%
  add_trace(x = ~date.time, y = ~`Flow compound weir stormflow clipped (gpm)`,
            name = 'Flow (gpm)',type = 'scatter',mode = 'lines',line=list(color='rgb(5, 71, 176)'))%>%
  layout(
          xaxis= list(range=Jun.obs.range,title="date"), 
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



July.obs.flow<- plot_ly(flow.df) %>%
  add_trace(x = ~date.time, y = ~`Flow compound weir stormflow clipped (gpm)`,name = 'Flow (gpm)',type = 'scatter',mode = 'lines',line=list(color='rgb(5, 71, 176)'))%>%
  layout(
          xaxis= list(range=July.obs.range), 
          yaxis= list(range=c(0,20),title="Flow (gpm)"),showlegend = FALSE
          )  %>%
  add_annotations(
          text = paste(site_id,"July Observation",sep = " "), x = 0.8,
          y = 1,yref = "paper",xref = "paper",xanchor = "middle",yanchor = "top",showarrow = FALSE,font = list(size = 10)
                  )

#July.obs.flow




######## Part 3. Start combining some plots dawg ####
Jun.Jul.obs <-subplot(Jun.obs.flow,July.obs.flow,shareY = TRUE,margin= 0.05)#, shareX = TRUE)
Jun.Jul.obs

may.jun.flow <-subplot(shareY = TRUE,nrows = 2,May.flow,Jun.flow)


recurs<-subplot(nrows=2,margin= 0.05,titleY = TRUE, titleX = FALSE, May.flow,Jun.Jul.obs,Jun.flow)
recurs

may.june.flow.obs<-subplot(nrows=1,margin= 0.05,titleY = TRUE, titleX = TRUE, may.jun.flow,Jun.Jul.obs)
may.june.flow.obs



#working plotly export
#export(next.month, file = "flow_reduction_plot.png")








############ old code ############

par(mfrow = c(1,1))
plot((flow.df$date.time),flow.df$`Flow compound weir stormflow clipped (gpm)`,type = "l",xlab = "Date",ylab = "Flow (gpm)",xlim = May, ylim = c(0,20),col="blue" ,xaxt="n")
axis.POSIXct(1,flow.df$date.time)
plot(flow.df$date.time,flow.df$`Flow compound weir stormflow clipped (gpm)`,type = "l",xlab = "Date",ylab = "Flow (gpm)",xlim = May.obs.range, ylim = c(0,20),col="blue" )



#same.months <-subplot(nrows=2,margin= 0.05,titleY = TRUE, titleX = TRUE, May.flow,May.obs.flow,Jun.flow,Jun.obs.flow)
#same.months

#next.month<-subplot(nrows=2,margin= 0.05,titleY = TRUE, titleX = TRUE, May.flow,Jun.obs.flow,Jun.flow,July.obs.flow)
#next.month

#plotly_IMAGE(next.month, width = 500, height = 500, format = "png", scale = 2,
        #     out_file = "~/desktop/test.png")


#hydro.ts=zoo(flow.df$, order.by = flow.df$date.time)

#plot.zoo(hydro.ts$date.time,hydro.ts$`Flow compound weir stormflow clipped (gpm) filled w median`,ylim =c(0,100))
