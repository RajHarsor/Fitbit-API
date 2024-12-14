# %%
import os
import json
import fitbit
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# %%
class FitbitAuthSimple:
    def __init__(self):
        load_dotenv()
        self.client_id = os.getenv('FITBIT_CLIENT_ID')
        self.client_secret = os.getenv('FITBIT_CLIENT_SECRET')
        # Use a dummy redirect URI - Fitbit will still show the code
        self.redirect_uri = os.getenv('FITBIT_REDIRECT_URI')
        self.token_file = 'user_tokens.json'

    def get_auth_link(self, user_id):
        """Generate authorization link for a participant"""
        client = fitbit.Fitbit(
            self.client_id,
            self.client_secret,
            redirect_uri=self.redirect_uri,
            oauth2=True
        )
        url, _ = client.client.authorize_token_url(
            scope=['activity', 'profile']
        )
        return url

    def save_token_from_code(self, user_id, auth_code):
        """Save token using auth code from URL"""
        client = fitbit.Fitbit(
            self.client_id,
            self.client_secret,
            redirect_uri=self.redirect_uri,
            oauth2=True
        )
        tokens = client.client.fetch_access_token(auth_code)
        self._save_tokens(user_id, tokens)
        return tokens

    def _save_tokens(self, user_id, tokens):
        all_tokens = self._load_all_tokens()
        all_tokens[user_id] = tokens
        with open(self.token_file, 'w') as f:
            json.dump(all_tokens, f)

    def _load_all_tokens(self):
        try:
            with open(self.token_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def get_user_steps(self, user_id, start_date, end_date=None):
        """Get step data for a user between dates
        start_date: YYYY-MM-DD string
        end_date: YYYY-MM-DD string (optional, defaults to today)
        """
        tokens = self._load_all_tokens().get(user_id)
        if not tokens:
            raise ValueError(f"No tokens found for user {user_id}")

        client = fitbit.Fitbit(
            self.client_id,
            self.client_secret,
            access_token=tokens['access_token'],
            refresh_token=tokens['refresh_token'],
            refresh_cb=lambda token: self._save_tokens(user_id, token),
            oauth2=True
        )

        try:
            if end_date:
                return client.time_series('activities/steps', 
                                        base_date=start_date,
                                        end_date=end_date)
            else:
                return client.time_series('activities/steps', 
                                        base_date=start_date,
                                        period='1d')
        except Exception as e:
            print(f"Error fetching steps: {e}")
            return None

    def extract_all_users_steps(self, json_file_path, start_date, end_date):
        # Read JSON file
        with open(json_file_path, 'r') as file:
            all_users_data = json.load(file)

        # Lists to store data
        all_data = []

        # Convert date strings to datetime objects
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')

        # Debug print
        print(f"Extracting data from {start_date} to {end_date}")

        # Loop through each user
        for user_id, user_data in all_users_data.items():
            print(f"Processing user: {user_id}")
            tokens = self._load_all_tokens().get(user_id)
            if not tokens:
                print(f"No tokens found for user {user_id}")
                continue

            client = fitbit.Fitbit(
                self.client_id,
                self.client_secret,
                access_token=tokens['access_token'],
                refresh_token=tokens['refresh_token'],
                refresh_cb=lambda token: self._save_tokens(user_id, token),
                oauth2=True
            )

            try:
                steps_data = client.time_series('activities/steps', base_date=start_date, end_date=end_date)
                for day in steps_data['activities-steps']:
                    date = datetime.strptime(day['dateTime'], '%Y-%m-%d')
                    print(f"Checking date: {day['dateTime']} (parsed: {date})")
                    if start <= date <= end:
                        all_data.append({
                            'user_id': user_id,
                            'date': day['dateTime'],
                            'steps': int(day['value'])
                        })
                        # Debug print
                        print(f"User: {user_id}, Date: {day['dateTime']}, Steps: {day['value']}")
            except Exception as e:
                print(f"Error retrieving data for user {user_id}: {e}")

        # Create DataFrame
        if all_data:
            df = pd.DataFrame(all_data)
            output_file = f'steps_data_{start_date}_to_{end_date}.csv'
            df.to_csv(output_file, index=False)
            print(f"Data exported to {output_file}")
            return df
        else:
            print("No data found for the specified date range")
            return None

# %%
# Usage
if __name__ == "__main__":
    auth = FitbitAuthSimple()

    option = input("What step would you like to do? \n1. Generate link for participant \n2. Save token from code \n3. Get single user steps for a certain range \n4. Extract all users data to a CSV file \n")

    match option:
        case "1": # Generate link for participant to authorize
            user_id = input("Enter the user_id: ")
            auth_link = auth.get_auth_link(user_id)
            print(f"\nGive this link to participant {user_id}:")
            print(auth_link)
        case "2": # Save token from code
            user_id = input("Enter the user_id: ")
            code = input("\nEnter the code from the URL: ")
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
        case _:
            print("Invalid option")

#TODO: Add a way to export all user data to a CSV file
#TODO: Add a way to get data for multiple users at once
#TODO: Storing method for JSON file