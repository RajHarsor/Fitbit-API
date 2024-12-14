# %%
import os
import json
import fitbit
import pandas as pd
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

# %%
# Usage
if __name__ == "__main__":
    auth = FitbitAuthSimple()

    option = input("What step would you like to do? \n1. Generate link for participant \n2. Save token from code \n3. Get single user steps for a certain range \n")

    match option:
        case "1":
            user_id = input("Enter the user_id: ")
            auth_link = auth.get_auth_link(user_id)
            print(f"\nGive this link to participant {user_id}:")
            print(auth_link)
        case "2":
            user_id = input("Enter the user_id: ")
            code = input("\nEnter the code from the URL: ")
            auth.save_token_from_code(user_id, code)
        case "3":
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
        case _:
            print("Invalid option")

#TODO: Add a way to export all user data to a CSV file
#TODO: Add a way to get data for multiple users at once
#TODO: Storing method for JSON file