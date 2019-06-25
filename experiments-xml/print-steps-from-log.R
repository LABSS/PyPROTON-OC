#!/usr/bin/env Rscript
args = commandArgs(trailingOnly=TRUE)
# test if there is at least one argument: if not, return an error
if (length(args)==0) {
  args[1]="netlogo.log"
} 

library(tidyverse, quietly=TRUE, warn.conflicts = FALSE, verbose = FALSE)

# not used
f <- args[1]

testload <-
readLines(pipe(paste0("tail -50 ", args[1], " | grep -v Time"))) %>%
gsub("observer: \\\"", "", .) %>%
gsub("\\\"", "", .) %>%
read.csv(text=., skip=6, header=TRUE, sep=".") %>%
set_names(., c("sim", "step")) %>%
group_by(sim) %>% 
slice(which.max(step)) %>%
ungroup() %>%
summarise(tot = sum(sim %/% 8 * 480 + step))

print(as.numeric(testload) )
