library(tidyverse)
library(readxl)

setwd(dirname(rstudioapi::getActiveDocumentContext()$path))

df <-
  file.path("raw", "net_authors_sex_age_conditional_proba.xlsx") %>%
  read_excel(sheet = "age_gender_probabilities", col_names = FALSE) %>%
 filter(row_number() == 1 | row_number() == 2 | row_number() == 12) %>%
 select( num_range("...", 7:16))

for(i in (1:10)) {
  l<-6
  df[1,i] <-  df[1,floor((i)/l)*(l-1)+1]
}

df2 <- as_tibble(t(df)) %>%
  rename(`male?`=V1, "age"=V2, "p"=V3) %>%
  mutate(  
    `male?` = if_else(`male?`=="female", FALSE, TRUE),
    p = as.numeric(p)
  )

df3<-df2 %>%
  mutate(
    age = case_when(
        age == "up to 13" ~ "0-13",
        age == "65 anni o più" ~ "65-200",
        TRUE ~ age 
      ),
    age =
      age %>%
      str_extract_all("\\d+") %>%
      map(as.numeric) %>%
      map((lift(seq)))
  ) %>%
  unnest(age) %>%
  select(`male?`,age,p) %>%
  write_csv(file.path("data", "crime_rate_by_gender_and_age.csv"))  

df4 <- df2 %>%
  mutate(
    "age_from" = str_extract_all(age, "\\d+", simplify = TRUE)[,1],
   "age_to" = str_extract_all(age, "\\d+", simplify = TRUE)[,2],
   age_from = as.numeric(age_from),
    age_to = as.numeric(age_to),
    age_to = case_when(
      is.na(age_to) ~ 200,
      TRUE ~ age_to
    )
  ) %>%
  select(`male?`,age_from,age_to,p) %>%
  write_csv(file.path("data", "crime_rate_by_gender_and_age_range.csv"))  