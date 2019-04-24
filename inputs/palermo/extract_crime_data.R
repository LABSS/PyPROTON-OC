library(tidyverse)
library(readxl)

setwd(dirname(rstudioapi::getActiveDocumentContext()$path))


df <-
  file.path("raw", "authors_sex_age_conditional_prob_ corretto.xlsx") %>%
  read_excel(sheet = "conditional_probability") %>%
  filter(between(row_number(), 11, 12)) %>%
  select(-Year) %>%
  gather(key=age, value="p", -Gender) %>%
  rename(`male?`=Gender)

df2<-df %>%
  mutate(
    age = case_when(
        age == "up to 13" ~ "0-13",
        age == "65+" ~ "65-200",
        TRUE ~ age 
      ),
    age =
      age %>%
      str_extract_all("\\d+") %>%
      map(as.numeric) %>%
      map((lift(seq))), 
    `male?` = if_else(`male?`=="Females",FALSE, TRUE),
    p = as.numeric(p)
  ) %>%
  unnest(age) %>%
  select(`male?`,age,p) %>%
  write_csv(file.path("data", "crime_rate_by_gender_and_age.csv"))  

df3 <- df %>%
  mutate(age = str_replace_all(age,"\\<|\\+", "")) %>%
  separate(age, into = c("age_from", "age_to"), sep = "-") %>%
  mutate(
    age_from = as.numeric(age_from),
    age_to = as.numeric(age_to),
    age_to = case_when(
      age_from == 13 ~ 13,
      age_from == 65 ~ 200,
      TRUE ~ age_to
    ),
    age_from = case_when(
      age_from == 13 ~ 0,
      TRUE ~ age_from
    ),
    `male?` = if_else(`male?`=="Female",FALSE, TRUE),
    p = as.numeric(p)
  ) %>%
  select(`male?`,age_from,age_to,p) %>%
  write_csv(file.path("data", "crime_rate_by_gender_and_age_range.csv"))  

