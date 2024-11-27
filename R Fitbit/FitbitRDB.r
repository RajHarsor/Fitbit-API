# Install additional required packages if needed
# install.packages(c("dotenv", "fitbitr", "RSQLite", "DBI"))

# Load required libraries
library(dotenv)
library(fitbitr)
library(lubridate)
library(RSQLite)
library(DBI)

load_dot_env()

# Initialize database connection
init_database <- function() {
    # Connect to SQLite database (will create if doesn't exist)
    con <- dbConnect(RSQLite::SQLite(), "fitbit_tokens.db")
    
    # Create tokens table if it doesn't exist
    dbExecute(con, "
        CREATE TABLE IF NOT EXISTS fitbit_tokens (
            user_id TEXT PRIMARY KEY,
            access_token TEXT,
            refresh_token TEXT,
            expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ")
    
    return(con)
}

# Function to generate authorization URL
generate_auth_url <- function(client_id, callback_url) {
    scope <- "activity heartrate location nutrition profile settings sleep social weight"
    base_url <- "https://www.fitbit.com/oauth2/authorize"
    
    auth_url <- sprintf(
        "%s?response_type=code&client_id=%s&redirect_uri=%s&scope=%s",
        base_url,
        client_id,
        utils::URLencode(callback_url),
        utils::URLencode(scope)
    )
    
    return(auth_url)
}

# Function to store token in database
store_token <- function(con, user_id, token) {
    query <- "
        INSERT OR REPLACE INTO fitbit_tokens 
        (user_id, access_token, refresh_token, expires_at) 
        VALUES (?, ?, ?, ?)
    "
    
    dbExecute(
        con,
        query,
        params = list(
            user_id,
            token$access_token,
            token$refresh_token,
            as.character(Sys.time() + token$expires_in)
        )
    )
}

# Function to retrieve token from database
get_stored_token <- function(con, user_id) {
    query <- "SELECT * FROM fitbit_tokens WHERE user_id = ?"
    result <- dbGetQuery(con, query, params = list(user_id))
    
    if (nrow(result) == 0) {
        return(NULL)
    }
    
    return(result)
}

# Main function to handle authorization and token storage
authorize_user <- function(user_id) {
    # Load environment variables
    load_dot_env()
    
    # Initialize database connection
    con <- init_database()
    on.exit(dbDisconnect(con))
    
    # Check if we already have a valid token
    stored_token <- get_stored_token(con, user_id)
    
    if (!is.null(stored_token) && as.POSIXct(stored_token$expires_at) > Sys.time()) {
        cat("Using existing valid token for user", user_id, "\n")
        return(stored_token)
    }
    
    # Generate new token
    cat("Generating new token for user", user_id, "\n")
    token <- generate_fitbitr_token(
        client_id = Sys.getenv("FITBIT_CLIENT_ID"),
        client_secret = Sys.getenv("FITBIT_CLIENT_SECRET"),
        callback = Sys.getenv("FITBIT_CALLBACK_URL")
    )
    
    # Store the token
    store_token(con, user_id, token)
    
    return(get_stored_token(con, user_id))
}

# Function to generate authorization links for multiple users
generate_auth_links <- function(user_ids) {
    client_id <- Sys.getenv("FITBIT_CLIENT_ID")
    callback_url <- Sys.getenv("FITBIT_CALLBACK_URL")
    
    auth_urls <- sapply(user_ids, function(user_id) {
        list(
            user_id = user_id,
            auth_url = generate_auth_url(client_id, callback_url)
        )
    })
    
    return(auth_urls)
}

# Example usage:
# Generate authorization links for multiple users
users <- c("Nelle")
auth_links <- generate_auth_links(users)
print(auth_links)

# When a user completes authorization, store their token
authorize_user("Nelle")

# Get steps data for a specific user
get_user_steps <- function(user_id, start_date, end_date) {
    con <- init_database()
    on.exit(dbDisconnect(con))
    
    token <- get_stored_token(con, user_id)
    if (is.null(token)) {
        stop("No token found for user ", user_id)
    }
    
    # Set the token in the fitbitr environment
    assign("fitbitr_token", token, envir = fitbitr:::.fitbitr)
    
    # Get steps data
    steps_data <- get_steps(start_date, end_date)
    return(steps_data)
}

# Example of getting steps data:
today <- today()
yesterday <- today - 1
steps_data <- get_user_steps("Angelica", yesterday, today)
print(steps_data)
