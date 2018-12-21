# extracts the SES data from BoI files created by UCSC
# creates 4 files for the cross distributions (3 keys, class, gender, and destination)
# creates 4 files for the marginal distributions (2 keys, class and gender)

library(tidyverse)

setwd(dirname(rstudioapi::getActiveDocumentContext()$path))

df <-
  file.path("raw", "CrimeYearlyByGenderAgePalermo.csv") %>%
  read_delim(" ") %>%
  select(c(1,4,3)) %>%
  rename("male?" = 1, "age" = 3, "p" = 2) %>%
  mutate(
    age =
      age %>%
      str_extract_all("\\d+") %>%
      map(as.numeric) %>%
      map((lift(seq))),
    `male?` = if_else(`male?`=="Female",FALSE, TRUE)
  ) %>%
  unnest(age) %>%
  write_csv(file.path("data", "crime_rate_by_gender_and_age.csv"))  

df <-
  file.path("raw", "CrimeYearlyByGenderAgePalermo.csv") %>%
  read_delim(" ") %>%
  select(c(1,4,3)) %>%
  rename("male?" = 1, "age" = 3, "p" = 2) %>%
  mutate(
    age_from =
      age %>%
      str_extract("\\d+") %>%
      map(as.numeric),
    age_to = 
      age %>%
      ifelse(length(str_extract_all(.,"\\d+")) > 1, str_extract_all(.,"\\d+")[[2]], ""),
    `male?` = if_else(`male?`=="Female",FALSE, TRUE)
  )


df <-
  file.path("raw", "CrimeYearlyByGenderAgePalermo.csv") %>%
  read_delim(" ") %>%
  select(c(1,4,3)) %>%
  rename("male?" = 1, "age" = 3, "p" = 2) %>%
  mutate(
    age_to = age %>%
      length(map(.,function(x)str_extract_all(x,"\\d+")))

  )


