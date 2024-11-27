import os
import json
import fitbit
from dotenv import load_dotenv

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
            scope=['activity', 'heartrate', 'sleep', 'profile']
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

# Usage example
if __name__ == "__main__":
    auth = FitbitAuthSimple()
    
    # Step 1: Generate link for participant
    # user_id = "participant123"
    # auth_link = auth.get_auth_link(user_id)
    # print(f"\nGive this link to participant {user_id}:")
    # print(auth_link)
    
    # Step 2: After participant clicks link and authorizes, they'll be redirected to a URL
    # The URL will contain the auth code like: http://localhost:8080?code=XXXX
    # Extract the code from URL and use it here:
    # code = input("\nEnter the code from the URL: ")
    # auth.save_token_from_code(user_id, code)
    
    # Step 3: Now you can use the Fitbit API with the saved token
    # Get steps for last 7 days
    from datetime import datetime, timedelta
    today = datetime.now().strftime('%Y-%m-%d')
    week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

    #TODO: Add a input for the user to input the user_id and replace "participant123" with the user_id
    steps_data = auth.get_user_steps("participant123", week_ago, today)
    print(steps_data)

#TODO: Add a way to export all user data to a CSV file
#TODO: Add a way to get data for multiple users at once
#TODO: Add a way for the user operating to choose the step they want to do in the pipeline
#TODO: Adjust the scopes to only get the data that is needed
#TODO: Extra testing to make sure the code works as expected w/ other users
#TODO: Storing method for JSON file