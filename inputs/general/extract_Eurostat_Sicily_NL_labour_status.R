library(tidyverse)
library(readxl)

setwd(dirname(rstudioapi::getActiveDocumentContext()$path))

df <-
  file.path("raw", "Eurostat_Sicily_NL_labour_status.xls") %>%
  read_excel(sheet = "Sicily",skip = 6, n_max = 10) %>%
  mutate(
    unemployed = (`2016__3`+ `2017__3` + `2018__3`) / 3 ,
    inactive = (`2016__4`+ `2017__4` + `2018__4`) / 3,
    inactive_ratio = inactive / (inactive + unemployed)
    ) %>%
  select("Sex", "age"= "Age class (years)", unemployed, inactive, inactive_ratio)

for(i in (1:10)) {
  l<-6
  df[i,1] <-  df[floor((i)/l)*(l-1)+1,1]
}

df <- df %>%
  mutate(
    `male?` = case_when(
      Sex == "Females" ~ "FALSE",
      TRUE ~ "TRUE"),
    age =
      age %>%
      str_extract_all("\\d+") %>%
      map(as.numeric) %>%
      map((lift(seq)))
  ) %>%
  unnest(age) %>%
  select(`male?`, "age", inactive_ratio) %>%
  write_csv(file.path("../palermo/data", "labour_status.csv"))  

