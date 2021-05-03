extensions = dict(
    set_required_params="""
parms$training_frame <- training_frame
args <- .verify_dataxy(training_frame, x, y)
parms$ignored_columns <- args$x_ignore
parms$response_column <- args$y
"""
)

doc = dict(
    preamble="""
H2O AnovaGLM is used to calculate Type III SS which is used to evaluate the contributions of individual predictors 
and their interactions to a model.  Predictors or interactions with negligible contributions to the model will have 
high p-values while those with more contributions will have low p-values. 
""",
    examples="""
lirary(h2o)
h2o.init()

# Run ANOVA GLM of VOL ~ CAPSULE + RACE
f <- "https://s3.amazonaws.com/h2o-public-test-data/smalldata/gbm_test/titanic.csv"
prostate <- h2o.uploadFile(f)
prostate$CAPSULE <- as.factor(prostate$CAPSULE)
model <- h2o.anovaglm(y = "VOL", x = c("CAPSULE", "RACE"), training_frame = prostate, family = "gaussian")
"""
)
