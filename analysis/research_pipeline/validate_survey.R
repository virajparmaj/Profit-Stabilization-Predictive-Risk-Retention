# Independent benchmark: R >=4.5, survey 4.5. Arguments: raw CSV, output CSV.
# Install survey in your own R library; no package installation occurs here.
args <- commandArgs(trailingOnly=TRUE)
if (length(args) != 2) stop("Usage: Rscript validate_survey.R raw.csv output.csv")
library(survey)
raw <- read.csv(args[1])
raw$analysis_weight <- ifelse(raw$SAQELIG == 1 & raw$AGE42X >= 18 &
                             raw$SAQWT23F > 0 & raw$PERWT23F > 0, raw$SAQWT23F, 0)
design <- svydesign(ids=~VARPSU, strata=~VARSTR, weights=~analysis_weight,
                    data=raw, nest=TRUE)
estimate <- svymean(~TOTEXP23, design)
result <- data.frame(implementation=paste("R survey", packageVersion("survey")),
                     mean=as.numeric(coef(estimate)), se=as.numeric(SE(estimate)))
write.csv(result, args[2], row.names=FALSE)
print(result)
