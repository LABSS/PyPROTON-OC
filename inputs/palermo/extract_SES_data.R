library(tidyverse)
library(readxl)

setwd(dirname(rstudioapi::getActiveDocumentContext()$path))

df <-
  file.path("raw", "SES mechanism  (without firing & hirings).xlsx") %>%
  read_excel(sheet = "4. Distribution_matrices") 

names(df)
for(i in c(
  "edu_by_wealth_lvl", 
  "work_status_by_edu_lvl",
  "wealth_quintile_by_work_status", 
  "criminal_propensity_by_wealth_quintile")) 
  {
  df1 <- 
    filter(df, `Distribution (compact name)` == i,
           `% / abs_val` == "%", 
           sex != "all", y != "SUM") %>%
    transmute(
      `x=1`,`x=2`,`x=3`,`x=4`,`x=5`,y,sex ) %>%
    gather(key = class, value =  rate, -sex, -y) %>%
    mutate(class= 
              class %>%
              str_extract("\\d+") %>%
              as.numeric(),
              y = as.numeric(y)
            ) %>%
    write_csv(file.path("data", paste(i,".csv",sep="")))
  }

