library(tidyverse)
library(lubridate)
library(readxl)

setwd(dirname(rstudioapi::getActiveDocumentContext()$path))

pattern <- ".*PROTON_Operazioni_(.*)_Stats.*.xlsx"
files <- list.files(file.path(".", "raw"), pattern, full.names = TRUE)

ref_date = today() # for calculating ages (TODO: use a fixed date?)

df <- files %>%
  map_dfr(function (file) {
    # consolidate data from the 1st sheet of every Excel files:
    read_excel(file, sheet = 1, na = c("N/A", "non affiliato")) %>%
    select(1:9) %>% # all the columns we need are among the first 9
    rename_all(tolower) %>% # because column name case is inconsistent
    # add a column with the operation name extracted from the file name:
    add_column(operation = str_match(file, pattern)[, 2])
  }) %>%
  # keep only the people convicted for mafia related offenses:
  filter(`occ 416bis` | occ_mafia_method) %>%
  mutate(
    birth_date = if_else(!is.na(date_birth),
      date(date_birth), # keep the birth date if we have
      ymd(year_birth, truncated = 2) # or just use the year otherwise
    ),
    age = as.duration(birth_date %--% ref_date) %/% as.duration(years(1)),
    group = as.numeric(as_factor(mafia_group)),
    family = as.numeric(as_factor(surname))
  ) %>%
  filter(!is.na(age)) %>% # exclude four ageless guys (TODO: impute instead?)
  select(
    operation, group, family, age
  )

  # take a quick look at age distributions...
  ggplot(df, aes(age)) + geom_histogram() + facet_wrap(vars(operation))

  write.csv(df, file = file.path("data", "oc_groups.csv"), row.names = FALSE)
