# %%
import os
import json
import fitbit
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs
import project_pace_api_functions as paf
import time
# %%
# Usage
if __name__ == "__main__":
    auth = paf.FitbitAuthSimple()

    print("Project Pace Text Database + Fitbit API")
    time.sleep(1)

    """ Initialization of Environment"""
    # Check if .env file exists
    print("Checking if .env file exists...")
    
    env_var_file = paf.check_env_file_exists()
    if not env_var_file: # If .env file does not exist, prompt user to create one
        print("No .env file found. Please create a .env file with your Fitbit API credentials.")
        print("Please setup the environment variables in the .env file as follows:")
        
        # Prompt user for input
        fitbit_client_id = input("FITBIT_CLIENT_ID: ")
        fitbit_client_secret = input("FITBIT_CLIENT_SECRET: ")
        tokens_path = input("TOKENS_PATH: ")
        info_path = input("INFO_PATH: ")
        aws_access_key_id = input("AWS_ACCESS_KEY_ID: ")
        aws_secret_access_key = input("AWS_SECRET_ACCESS_KEY: ")
        paf.create_env_file(fitbit_client_id,
                            fitbit_client_secret,
                            tokens_path=tokens_path,
                            info_path=info_path,
                            aws_access_key_id=aws_access_key_id,
                            aws_secret_access_key=aws_secret_access_key)
        print("Created .env file. Reload the script to continue.")
        exit(1)
    else:
        print("Found .env file. Checking environment variables...")
        req_env_vars = paf.check_env_variables()
        if req_env_vars[0] == False: # If the required vars[0] is False, it means some variables are missing
            print(f"Missing environment variables: {req_env_vars[1]}")

            # For loop through the missing variables and prompt user to input them
            # Split the missing variables by comma
            req_env_vars_missing = req_env_vars[1].split(',')
            for var in req_env_vars_missing:
                value = input(f"Enter value for {var}: ")
                with open('.env', 'a') as f:
                    f.write(f"{var}={value}\n")
            print("Updated .env file with missing variables. Reload the script to continue.")
            exit(1)
        else:
            print("All required environment variables are set.")

    """ Options for user interaction """
    print("What step would you like to do? \n1. Generate link for participant & save token \n2. Get single user steps for a certain range \n3. Extract all users data to a CSV file from a date range \n4. Extract all users data according to the study period \n5. Delete a user \n6. Get sleep data over the study period\n7. Get activity data over the study period\n8. Update environment variable\n9. Exit")

    option = input("Enter the number of the option you want to execute: ")
    
    match option:
        case "1": # Generate link for participant to authorize
            user_id = input("Enter the user_id: ")
            auth_link = auth.get_auth_link()
            print(f"\nGive this link to participant {user_id}:")
            print(auth_link)
            link_code = input("\nInput URL that the participant recieved: ")
            parsed_url = urlparse(link_code)
            code = parse_qs(parsed_url.query)['code'][0]
            auth.save_token_from_code(user_id, code)
        case "2": # Get steps for a user up to a certain amount of days back
            user_id = input("Enter the user_id: ")
            days = int(input("Enter the number of days you want to look back: "))
            from datetime import datetime, timedelta
            today = datetime.now().strftime('%Y-%m-%d')
            time_ago = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            steps_data = auth.get_user_steps(user_id, time_ago, today)

            # Convert to DataFrame
            if steps_data and 'activities-steps' in steps_data:
                df = pd.DataFrame(steps_data['activities-steps'])
                df.columns = ['Date', 'Steps']  # Rename columns
                df['Steps'] = df['Steps'].astype(int)  # Convert steps to integers
                print("\nSteps Data:")
                print(df)
            else:
                print("No data available")
        case "3": # Extract all users data to a CSV file from a certain date to a certain date
                start_date = input("Enter start date (YYYY-MM-DD): ")
                end_date = input("Enter end date (YYYY-MM-DD): ")
                result_df = auth.extract_all_users_steps('user_tokens.json', start_date, end_date)
                if result_df is not None:
                    print("\nExtracted Data:")
                    print(result_df)
        case "4": # Extract all users data according to the study period
            result_df = auth.extract_all_users_steps_study_period()
            if result_df is not None:
                print("\nExtracted Data:")
                print(result_df)
        case "5": # Delete user
            user_id = input("Enter the user_id you want to delete: ")
            auth.delete_user(user_id)
        case "6": # Get sleep data
            result_df = auth.extract_all_users_sleepData_study_period()
            if result_df is not None:
                print("\nExtracted Data:")
                print(result_df)
        case "7": # Get activity data
            result_df = auth.extract_all_users_activity_study_period()
            if result_df is not None:
                print("\nExtracted Data:")
                print(result_df)
        case "8": # Update env file
            paf.update_env_file()
        case "9": # Exit the program
            print("Exiting the program.")
            exit(1)
        case _:
            print("Invalid option")