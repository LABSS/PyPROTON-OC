library(tidyverse)
library(readxl)

setwd(dirname(rstudioapi::getActiveDocumentContext()$path))

df <-
  file.path("raw", "household-init-data.xlsx") %>%
  read_excel(sheet = "1a") %>%
  transmute(
    age = as.numeric(Age), # turns "100+" and "Total" rows into NA
    true = `P(A = a, gender = M)`,
    false = `P(A = a, gender = F)`
  ) %>%
  na.omit() %>%
  gather(`male?`, p, -age) %>%
  write_csv(file.path("data", "initial_age_gender_dist.csv"))

# show a population pyramid, just to check if the data makes sense
df %>%
  mutate(p = ifelse(`male?`, p, -p)) %>%
  ggplot(aes(x = age, y = p, fill = `male?`)) + geom_col() + coord_flip()
