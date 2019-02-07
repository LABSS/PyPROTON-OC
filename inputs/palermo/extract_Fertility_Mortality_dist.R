library(tidyverse)
library(readxl)

setwd(dirname(rstudioapi::getActiveDocumentContext()$path))

df <-
  file.path("raw", "Fertility and Mortality rates.xlsx") %>%
  read_excel(sheet = "1") %>%
  transmute(
    age = `Age group`,
    true = 1 - `Prospective probability of living (Males)`,
    false = 1 - `Prospective probability of living (Females)`
  ) %>%
  na.omit() %>%
  filter(str_detect(age, "\\d")) %>%
  mutate(
    age =
      age %>%
      str_extract_all("\\d+") %>%
      map(as.numeric) %>%
      map((lift(seq)))
  ) %>%
  unnest(age) %>%
  gather(`male?`, p, -age) %>%
  write_csv(file.path("data", "initial_mortality_rates.csv"))


df <-
  file.path("raw", "Fertility and Mortality rates.xlsx") %>%
  read_excel(sheet = "2") %>%
  transmute(
    age = `Ordine di nascita`,
    "0" = `first child`,
    "1" = `second child`,
    "2" = `third child`
  ) %>%
  mutate(
    age = case_when(
        age == "50 +" ~ "50",
        TRUE ~ age 
      )
  ) %>%
  na.omit() %>%
  filter(age!='total' & age != '10-13 anni') %>%
  gather(num_children, fertility, -age) %>%
  write_csv(file.path("data", "initial_fertility_rates.csv"))

