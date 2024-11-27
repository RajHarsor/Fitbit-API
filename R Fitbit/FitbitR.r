# Install packages if needed
# install.packages(c("dotenv", "fitbitr"))

# Load required libraries
library(dotenv)
library(fitbitr)
library(lubridate)

# Today's date usiing lubridate
today <- today()
yesterday <- today - 1

# Load environment variables
load_dot_env()

# Generate the token with correct function name
cat("Attempting to authenticate with Fitbit...\n")
fitbitr_token <- generate_fitbitr_token(
    client_id = Sys.getenv("FITBIT_CLIENT_ID"),
    client_secret = Sys.getenv("FITBIT_CLIENT_SECRET"),
    callback = Sys.getenv("FITBIT_CALLBACK_URL"),
)

# Test if authentication worked by getting profile data
tryCatch({
    profile <- get_steps(yesterday, today)
    cat("\nAuthentication successful! Here's your profile data:\n")
    print(profile)
}, error = function(e) {
    cat("\nError occurred during authentication:\n")
    print(e)
})

