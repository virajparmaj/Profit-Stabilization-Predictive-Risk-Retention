# Validate fixed-ensemble reference disagreement linearization using survey.
# Input includes the full raw PSU design, zero weights outside reference people.
args <- commandArgs(trailingOnly=TRUE)
if (length(args) != 2) stop("Usage: Rscript validate_membership.R input.csv output.csv")
library(survey)
d <- read.csv(args[1])
s <- svydesign(ids=~VARPSU, strata=~VARSTR, weights=~weight, data=d, nest=TRUE)
m <- svymean(~contrast, s)
result <- data.frame(implementation=paste("R survey",packageVersion("survey")),
                     mean=as.numeric(coef(m)),se=as.numeric(SE(m)))
write.csv(result,args[2],row.names=FALSE)
print(result)
