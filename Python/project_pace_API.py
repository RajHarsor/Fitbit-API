# %%
import os
import json
import fitbit
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import project_pace_api_functions as paf
# %%
# Usage
if __name__ == "__main__":
    auth = paf.FitbitAuthSimple()

    option = input("What step would you like to do? \n1. Generate link for participant \n2. Save token from code \n3. Get single user steps for a certain range \n4. Extract all users data to a CSV file from a date range \n5. Extract all users data according to the study period \n6. Delete a user \n7. Get sleep data over the study period\n")

    match option:
        case "1": # Generate link for participant to authorize
            user_id = input("Enter the user_id: ")
            auth_link = auth.get_auth_link(user_id)
            print(f"\nGive this link to participant {user_id}:")
            print(auth_link)
        case "2": # Save token from code
            user_id = input("Enter the user_id: ")
            code = input("\nEnter the code from the URL: ")
            # TODO: URL Parse to get code
            auth.save_token_from_code(user_id, code)
        case "3": # Get steps for a user up to a certain amount of days back
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
        case "4": # Extract all users data to a CSV file from a certain date to a certain date
                start_date = input("Enter start date (YYYY-MM-DD): ")
                end_date = input("Enter end date (YYYY-MM-DD): ")
                result_df = auth.extract_all_users_steps('user_tokens.json', start_date, end_date)
                if result_df is not None:
                    print("\nExtracted Data:")
                    print(result_df)
        case "5": # Extract all users data according to the study period
            result_df = auth.extract_all_users_steps_study_period()
            if result_df is not None:
                print("\nExtracted Data:")
                print(result_df)
        case "6": # Delete user
            user_id = input("Enter the user_id you want to delete: ")
            auth.delete_user(user_id)
        case "7": # Get sleep data
            result_df = auth.extract_all_users_sleepData_study_period()
            if result_df is not None:
                print("\nExtracted Data:")
                print(result_df)
        case _:
            print("Invalid option")

# TODO: Sleep data
# TODO: Activity data