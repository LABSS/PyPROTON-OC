library(tidyverse)
library(readxl)

setwd(dirname(rstudioapi::getActiveDocumentContext()$path))

file <- file.path("raw", "household-init-data.xlsx")

min_age_of_head <- 18

df_size_dist <-
  read_excel(file, sheet = "4") %>%
  filter(.[[1]] == "Total") %>%
  select(matches("^\\d+$")) %>%
  gather(size, p) %>%
  mutate(size = as.numeric(size), p = p / sum(p)) %>%
  write_csv(file.path("data", "household_size_dist.csv"))

df_age_by_size_dist <-
  read_excel(file, sheet = "4") %>%
  select(age = starts_with("age"), matches("P.*=")) %>%
  mutate(age = as.numeric(age)) %>%
  filter(age >= min_age_of_head) %>%
  gather(size, p, -age) %>%
  transmute(size = as.numeric(str_extract(size, "\\d+")), age, p) %>%
  write_csv(file.path("data", "head_age_dist_by_household_size.csv"))

df_hh_type_by_age <-
  read_excel(file, sheet = "6") %>%
  rename(type = "Typology \\ age of reference person") %>%
  mutate(type = str_match(type, "P\\(([a-z_]+).*")[, 2]) %>%
  na.omit() %>%
  gather(age, p, -type) %>%
  transmute(age = as.numeric(age), type, p = as.numeric(p)) %>%
  filter(age >= min_age_of_head) %>%
  write_csv(file.path("data", "household_type_by_age_dist.csv"))

df_partner_age_dist <-
  read_excel(file, sheet = "7") %>%
  # Note that despite what the header in cell A1 says,
  # rows are ages of heads and columns are ages of partners
  select(age_of_head = 1, (match("P(a_r’|a_r =", names(.)) + 1):ncol(.)) %>%
  mutate(age_of_head = as.numeric(age_of_head)) %>%
  filter(age_of_head >= min_age_of_head) %>%
  gather(age_of_partner, p, -age_of_head) %>%
  mutate(age_of_partner = as.numeric(str_extract(age_of_partner, "\\d+"))) %>%
  write_csv(file.path("data", "partner_age_dist.csv"))

df_children_age_dist <-
  read_excel(file, sheet = "8") %>%
  select(
    child_number = `number of children`,
    age_of_mother = `age of mother`,
    age_of_child = `age of child`,
    p = `P(a_i | a_m = eta_madre, s = numero figli)`
  ) %>%
  write_csv(file.path("data", "children_age_dist.csv"))

# The proportion of single-parent households where the head is male
# was given by Emanuela Furfaro by email (2018-10-02)
write_file("0.1536", file.path("data", "proportion_single_fathers.csv"))
