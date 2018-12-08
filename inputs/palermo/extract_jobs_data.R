# extracts the jobs data BoI files created by UCSC


# creates 4 files for the cross distributions (3 keys, class, gender, and destination)
# creates 4 files for the marginal distributions (2 keys, class and gender)

require(tidyverse)
require(readxl)
setwd(dirname(rstudioapi::getActiveDocumentContext()$path))

df <-
  file.path("raw", "2. Job qualifications + education level (private + public).xlsx") %>%
  read_excel(sheet = "1. SES CATEGORIES") 

names(df)[4:16]
df1 <- 
  filter(df, row_number() == 2 | between(row_number(), 11, 13)) %>%
  select(X__1, num_range("X__", 3:15))
# we need to save df1 at this point because it's nested below
 df2 <-
  rename_at(df1, names(df)[4:16],  
              ~ df1 %>%      
              filter(X__1 == "Private companies")  %>%
              select(-X__1)
  ) %>%
  gather(key=class, value =  rate, -X__1) %>%
  filter(X__1 != "Private companies")
 
 df3 <-
  # mutate(df2,
  #   size = map(str_extract_all(class,"\\d+"), as.numeric)
  #   ) %>%
    mutate(df2,
      size = map(
        map (str_extract_all(class,"\\d+"), as.numeric),
        function(x){
          if(length(x)>1) lift(seq)(x) else x
        }),
      level = str_extract(X__1, "\\d+")
   ) %>%
   unnest(size) %>%
   select(size, level, rate) %>%
   write_csv(file.path("data", "jobs_by_company_size.csv"))

 #      class %>%
 #      %T>%
 #      print(.) %>%
 #      map(as.numeric)  %>%
 #     map ({if(length(.)>1) (map((lift(seq)),.)) else .}),
 #  #    map(lift(seq)) ,
 #    level = str_extract(X__1, "\\d+"),
 #  ) 
 # 
 # 
 # 
 #  
 # df3 <-
 #  mutate(df2,
 #    size = str_extract_all(class,"\\d+") 
 #      class %>%
 #      %T>%
 #      print(.) %>%
 #      map(as.numeric)  %>%
 #     map ({if(length(.)>1) (map((lift(seq)),.)) else .}),
 #  #    map(lift(seq)) ,
 #    level = str_extract(X__1, "\\d+"),
 #  ) 
 # 
 # 
 # 
 #  unnest(size) %>%
 #  select(-class, -X__1)
 #  
 #  
