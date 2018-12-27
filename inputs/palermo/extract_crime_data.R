# extracts the SES data from BoI files created by UCSC
# creates 4 files for the cross distributions (3 keys, class, gender, and destination)
# creates 4 files for the marginal distributions (2 keys, class and gender)

library(tidyverse)

setwd(dirname(rstudioapi::getActiveDocumentContext()$path))
rm(df)
df <-
  file.path("raw", "CrimeYearlyByGenderAgePalermo.csv") %>%
  read_csv(col_names=TRUE) %>%
  rename("male?" = 1, "age" = 2, "p" = 3)

df2<-df %>%
  #select(c(1,4,3)) %>%
  mutate(
    age = case_when(
        age == "<13" ~ "0-13",
        age == "65+" ~ "65-200",
        TRUE ~ age 
      ),
    age =
      age %>%
      str_extract_all("\\d+") %>%
      map(as.numeric) %>%
      map((lift(seq))), 
    `male?` = if_else(`male?`=="Female",FALSE, TRUE),
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

