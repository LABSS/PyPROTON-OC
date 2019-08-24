# Things we got from the NL data:

  set punishment-length-list read-csv "conviction_length.csv"
  set c-range-by-age-and-sex group-couples-by-2-keys read-csv "crime_rate_by_gender_and_age_range"
  set c-by-age-and-sex group-by-first-two-items read-csv "crime_rate_by_gender_and_age"
  let job-counts reduce sentence read-csv "employer_sizes" 
  let head-age-dist group-by-first-item read-csv "head_age_dist_by_household_size"
  let hh-type-dist group-by-first-item read-csv "household_type_dist_by_age"
  let hh-size-dist read-csv "household_size_dist"
  let age-gender-dist read-csv "initial_age_gender_dist"
  set labour-status-by-age-and-sex group-by-first-two-items read-csv "labour_status"
  set labour-status-range group-by-first-two-items read-csv "labour_status_range"
  let proportion-of-male-singles-by-age table:from-list read-csv "proportion_of_male_singles_by_age"
  let p-single-father first first csv:from-file (word data-folder "proportion_single_fathers.csv")
 

# Things that we recycle from palermo setup:
  let csv-data read-csv "../../palermo/data/children_age_dist"

  set edu group-by-first-of-three read-csv "../../palermo/data/edu"
  set edu_by_wealth_lvl group-couples-by-2-keys read-csv "../../palermo/data/edu_by_wealth_lvl"
  set fertility-table group-by-first-two-items read-csv "../../palermo/data/initial_fertility_rates"
  set mortality-table group-by-first-two-items read-csv "../../palermo/data/initial_mortality_rates"
  set jobs_by_company_size table-map table:group-items read-csv "../../palermo/data/jobs_by_company_size" [ line -> first line  ]   [ rows -> map but-first rows ]
  let list-schools read-csv "../../palermo/data/schools"
  let partner-age-dist group-by-first-item read-csv "../../palermo/data/partner_age_dist"
  set wealth_quintile_by_work_status group-couples-by-2-keys read-csv "../../palermo/data/wealth_quintile_by_work_status"
  set work_status_by_edu_lvl group-couples-by-2-keys read-csv "../../palermo/data/work_status_by_edu_lvl"

# Things we recycle from general setup:

 let marr item 0 but-first csv:from-file "inputs/general/data/marriages_stats.csv"
 set num-co-offenders-dist but-first csv:from-file "inputs/general/data/num_co_offenders_dist.csv"

# list of all non-general files

children_age_dist.csv
conviction_length.csv
crime_rate_by_gender_and_age.csv
crime_rate_by_gender_and_age_range.csv
edu.csv
edu_by_wealth_lvl.csv
employer_sizes.csv
head_age_dist_by_household_size.csv
household_size_dist.csv
household_type_dist_by_age.csv
initial_age_gender_dist.csv
initial_fertility_rates.csv
initial_mortality_rates.csv
jobs_by_company_size.csv
labour_status.csv
labour_status_range.csv
partner_age_dist.csv
proportion_of_male_singles_by_age.csv
proportion_single_fathers.csv
schools.csv
wealth_quintile.csv
wealth_quintile_by_work_status.csv
work_status.csv
work_status_by_edu_lvl.csv


