# extracts the SES data from BoI files created by UCSC
# creates 4 files for the cross distributions (3 keys, class, gender, and destination)
# creates 4 files for the marginal distributions (2 keys, class and gender)

library(tidyverse)
library(readxl)
setwd(dirname(rstudioapi::getActiveDocumentContext()$path))

df <-
  file.path("raw", "SES mechanism  (without firing & hirings).xlsx") %>%
  read_excel(sheet = "4. Distribution_matrices") 

ymeans <- c("wealth", "edu_level", "work_status", "wealth")
xmeans <- c("edu_level", "work_status", "wealth", "criminal_propensity")
tablename <- c("edu_by_wealth_lvl", 
  "work_status_by_edu_lvl",
  "wealth_quintile_by_work_status", 
  "criminal_propensity_by_wealth_quintile")
marginalname <- lapply( tablename,
  function(x){paste(
    strsplit(x, "_")[[1]][
      1:(length(strsplit(x, "_")[[1]])-3)
    ], collapse = "_"
  )}
 )

names(df)
for(i in  1:length(tablename))
  {
  df1 <- 
    filter(df, `Distribution (compact name)` == tablename[i],
           `% / abs_val` == "%", 
           sex != "all", y != "SUM") %>%
    transmute(
      `x=1`,`x=2`,`x=3`,`x=4`,`x=5`,y, 
    gender = ifelse(sex == "M", TRUE, FALSE) ) %>%
    gather(key = class, value =  rate, -gender, -y) %>%
    mutate(class= 
              class %>%
              str_extract("\\d+") %>%
              as.numeric(),
              y = as.numeric(y)
            ) %>%
    rename(!! sym(ymeans[i]) := y,
           !! sym(xmeans[i]) := class)  %>%  # pure magic. Required 20 attempts to guess.
    write_csv(file.path("data", paste(tablename[i],".csv",sep="")))
  }

for(i in  1:length(marginalname))
  {
  df1 <- 
    filter(df, `Distribution (compact name)` == tablename[i],
           `% / abs_val` == "%", 
           sex != "all", y != "SUM") %>%
    transmute(
      `SUM`,y, 
    gender = ifelse(sex == "M", TRUE, FALSE) ) %>%
    select(gender, !! sym(xmeans[i]) := y,
           rate = SUM) %>% # !! sym pure magic. Required 20 attempts to guess.
    write_csv(file.path("data", paste(marginalname[i],".csv",sep="")))
  }

