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

# show a population pyramid, just to check if the data makes sense
df %>%
  mutate(p = ifelse(`male?`, p, -p)) %>%
  ggplot(aes(x = age, y = p, fill = `male?`)) + geom_col() + coord_flip()
