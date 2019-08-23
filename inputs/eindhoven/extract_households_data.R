library(tidyverse)
library(readxl)

setwd(dirname(rstudioapi::getActiveDocumentContext()$path))

file <- file.path("raw", "data Eindhoven Proton.xlsx")

min_age_of_head <- 18
max_age_of_head <- 102 # because that's the max for which we have partner ages (only for palermo, tho)

df_size_dist <-
  read_excel(file, sheet = "4", skip = 1) %>%
  filter(.[[1]] == "Total") %>%
  select(matches("^\\d+$")) %>%  
  gather(size, p) %>%
  mutate(size = as.numeric(size)) %>%
  filter(size <= 9) %>% # because we can only generate max. 8 children
  mutate(p = p / sum(p)) %>%
  write_csv(file.path("data", "household_size_dist.csv"))

df_age_by_size_dist <-
  read_excel(file, sheet = "4", skip = 1) %>%
  rename(age = "...2") %>%
  select(-"...1") %>%
  mutate(age = as.numeric(age)) %>%
  filter(age >= min_age_of_head & age <= max_age_of_head) %>%
  gather(size, p, -age) %>%
  group_by(size) %>%
  mutate(p= p / sum(p) ) %>%
  write_csv(file.path("data", "head_age_dist_by_household_size.csv"))

df_hh_type_by_age <-
  read_excel(file, sheet = "6") %>%
  rename(type = `Age`) %>%
  filter(type != "single" & type != "Total") %>%
  na.omit() %>%
  gather(age, p, -type) %>%
  group_by(age) %>%
  mutate(p = p / sum(p)) %>%
  ungroup() %>%
  transmute(age = as.numeric(age), type, p = as.numeric(p)) %>%
  filter(age >= min_age_of_head) %>%
  write_csv(file.path("data", "household_type_dist_by_age.csv"))

# no data
# df_partner_age_dist <-
#   read_excel(file, sheet = "7") %>%
#   # Note that despite what the header in cell A1 says,
#   # rows are ages of heads and columns are ages of partners
#   select(age_of_head = 1, (match("P(a_r’|a_r =", names(.)) + 1):ncol(.)) %>%
#   mutate(age_of_head = as.numeric(age_of_head)) %>%
#   filter(age_of_head >= min_age_of_head) %>%
#   gather(age_of_partner, p, -age_of_head) %>%
#   mutate(age_of_partner = as.numeric(str_extract(age_of_partner, "\\d+"))) %>%
#   write_csv(file.path("data", "partner_age_dist.csv"))

# no data
# df_children_age_dist <-
#   read_excel(file, sheet = "8") %>%
#   select(
#     child_number = `number of children`,
#     age_of_mother = `age of mother`,
#     age_of_child = `age of child`,
#     p = `P(a_i | a_m = eta_madre, s = numero figli)`
#   ) %>%
#   write_csv(file.path("data", "children_age_dist.csv"))

# The proportion of single-parent households where the head is male
# was given by Emanuela Furfaro by email (2018-10-02)
write_file("0.1536", file.path("data", "proportion_single_fathers.csv"))
