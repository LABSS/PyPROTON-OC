library(tidyverse)
library(readxl)

setwd(dirname(rstudioapi::getActiveDocumentContext()$path))

df <-
  file.path("raw", "data Eindhoven Proton.xlsx") %>%
  read_excel(sheet = "1a", col_names = FALSE) %>%
 filter(row_number() > 2  & row_number() < 109) %>%
 select( num_range("...", c(2,3,5))) %>%
  rename(age="...2", m="...3", f="...5") %>%
  transmute(
    age = as.numeric(age), # turns "100+" and "Total" rows into NA
    m = as.numeric(m),
    f = as.numeric(f),
    true = m / (sum(m) + sum(f)),
    false = f / (sum(m) + sum(f))
  ) %>%
  select(age, true, false) %>%
  na.omit() %>%
  gather(`male?`, p, -age) %>%
  write_csv(file.path("data", "initial_age_gender_dist.csv"))

# show a population pyramid, just to check if the data makes sense
df %>%
  mutate(p = ifelse(`male?`, p, -p)) %>%
  ggplot(aes(x = age, y = p, fill = `male?`)) + geom_col() + coord_flip()
