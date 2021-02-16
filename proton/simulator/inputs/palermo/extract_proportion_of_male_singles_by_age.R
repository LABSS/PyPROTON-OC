library(tidyverse)
library(readxl)

setwd(dirname(rstudioapi::getActiveDocumentContext()$path))

max_age <- 108 # because it's the max we have in household init data

df <-
  file.path("raw", "single-by-gender.xlsx") %>%
  read_excel() %>%
  transmute(
    age = `Age group of the reference person`,
    p_male = Males / Total
  ) %>%
  filter(str_detect(age, "\\d")) %>%
  mutate(
    age =
      if_else(str_detect(age, "above"), str_glue("{age} {max_age}"), age) %>%
        str_extract_all("\\d+") %>%
        map(as.numeric) %>%
        map((lift(seq)))
  ) %>%
  unnest(age) %>%
  select(age, p_male) %>%
  write_csv(file.path("data", "proportion_of_male_singles_by_age.csv"))

# Woah, old singles are overwhelmingly female, it seems...
ggplot(df, aes(age, p_male)) + geom_line()
