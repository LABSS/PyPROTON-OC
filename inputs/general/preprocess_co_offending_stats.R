library(tidyverse)
library(readxl)

setwd(dirname(rstudioapi::getActiveDocumentContext()$path))

df <-
  file.path("raw", "co_offending_statistics_v3.xlsx") %>%
  read_excel(sheet = "Summary", na = "NA") %>%
  rename(n = 1) %>%
  filter(str_detect(n, "\\d+\\+?$")) %>%
  gather(study, p, -n) %>%
  mutate(
    n = as.numeric(str_extract(n, "\\d+")),
    p = as.numeric(p) / 100
  ) %>%
  filter( # exclude values of fused Excel cells
    !(study == "Carrington 2013" & n == 3),
    !(study == "Hodgson and Costello 2006" & n == 4)
  ) %>%
  na.omit()

# Hey, this looks a bit like a power law!
df %>%
  ggplot(aes(n, p, colour = study)) +
  geom_point() + scale_x_log10() + scale_y_log10()

# But I'm being quick and dirty here and just taking averages:
df <- df %>%
  group_by(n) %>%
  summarise(p = mean(p)) %>%
  mutate(p = p / sum(p)) %>%
  write_csv(file.path("data", "num_co_offenders_dist.csv"))

# R has a `poweRlaw` package (https://cran.r-project.org/package=poweRlaw)
# that could be used to fit an actual power law to that data.
# It might be worth the effort at some point...
