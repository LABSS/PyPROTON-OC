library(tidyverse)
library(readxl)

setwd(dirname(rstudioapi::getActiveDocumentContext()$path))


df <-
  file.path("raw", "Eurostat_Sicily_NL_labour_status_v2.xls") %>%
  read_excel(sheet = "Sicily",skip = 6, n_max = 10)

# this is to make it compatible with old versions of read_excel
ifelse("2016...9" %in% names(df),
    df <- mutate(df,
    unemployed = (`2016...12`+ `2017...13` + `2018...14`) / 3 ,
    inactive = (`2016...15`+ `2017...16` + `2018...17`) / 3
    ),
    df <- mutate(df,
    unemployed = (`2016__3`+ `2017__3` + `2018__3`) / 3 ,
    inactive = (`2016__4`+ `2017__4` + `2018__4`) / 3
    )
)
    df <- mutate(df,
    inactive_ratio = inactive / (inactive + unemployed)
    ) %>%
  select("Sex", "age"= "Age class (years)", unemployed, inactive, inactive_ratio)

for(i in (1:10)) {
  l<-6
  df[i,1] <-  df[floor((i)/l)*(l-1)+1,1]
}

df1 <- df %>%
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


df2 <- df %>%
  mutate(
    `male?` = case_when(
      Sex == "Females" ~ "FALSE",
      TRUE ~ "TRUE")) %>%
  separate(age, into = c("age_from", "age_to"), sep = "-") %>%
  select(`male?`, "age_from", inactive_ratio) %>%
  write_csv(file.path("../palermo/data", "labour_status_range.csv"))  


#### and now the netherlands

df <-
  file.path("raw", "Eurostat_Sicily_NL_labour_status_v2.xls") %>%
  read_excel(sheet = "NL",skip = 6, n_max = 20)

# this is to make it compatible with old versions of read_excel
ifelse("2016...9" %in% names(df),
    df <- mutate(df,
    unemployed = (`2016...9`+ `2017...10` + `2018...11`) / 3 ,
    inactive = (`2016...12`+ `2017...13` + `2018...14`) / 3
    ),
# untested
    df <- mutate(df,
    unemployed = (`2016__9`+ `2017__10` + `2018__11`) / 3 ,
    inactive = (`2016__12`+ `2017__13` + `2018__14`) / 3
    )
)
    df <- mutate(df,
    inactive_ratio = inactive / (inactive + unemployed)
    ) %>%
  select("Sex", "age"= "Age class (years)", unemployed, inactive, inactive_ratio)

for(i in (1:length(df$Sex))) {
  l<-length(df$Sex)/2+1
  df[i,1] <-  df[floor((i)/l)*(l-1)+1,1]
}

df1 <- df %>%
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
  write_csv(file.path("../eindhoven/data", "labour_status.csv"))  


df2 <- df %>%
  mutate(
    `male?` = case_when(
      Sex == "Females" ~ "FALSE",
      TRUE ~ "TRUE")) %>%
  separate(age, into = c("age_from", "age_to"), sep = "-") %>%
  select(`male?`, "age_from", inactive_ratio) %>%
  write_csv(file.path("../eindhoven/data", "labour_status_range.csv"))  
