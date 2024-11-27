import fitbit
from fitbit.api import Fitbit
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError
from requests_oauthlib import OAuth2Session
import datetime
import pandas as pd

# Your Fitbit app credentials
CLIENT_ID = '23PQ52'
CLIENT_SECRET = '3f7fab3653c057ddea29631f63caba38'

# Fitbit API endpoint
TOKEN_URL = "https://api.fitbit.com/oauth2/token"
AUTH_URL = "https://www.fitbit.com/oauth2/authorize"

# Callback URL (must match the one you set in your Fitbit app settings)
CALLBACK_URL = "https://127.0.0.1:8080/"

# Scopes (permissions) you're requesting
SCOPES = ["activity", "sleep", "heartrate", "profile"]

def get_new_access_token(client_id, client_secret, refresh_token):
    oauth = OAuth2Session(client_id=client_id, token={'refresh_token': refresh_token})
    new_token = oauth.refresh_token(TOKEN_URL, client_id=client_id, client_secret=client_secret)
    return new_token

def save_tokens(token):
    # In a real application, you should securely store these tokens
    # For this example, we'll just print them
    print("Access Token:", token['access_token'])
    print("Refresh Token:", token['refresh_token'])

def authenticate():
    oauth = OAuth2Session(CLIENT_ID, redirect_uri=CALLBACK_URL, scope=SCOPES)
    authorization_url, _ = oauth.authorization_url(AUTH_URL)
    print(f'Please go to this URL to authorize the application: {authorization_url}')
    
    redirect_response = input('Paste the full redirect URL here: ')
    token = oauth.fetch_token(TOKEN_URL, client_secret=CLIENT_SECRET, authorization_response=redirect_response)
    save_tokens(token)
    return token

def main():
    try:
        # Try to use existing tokens (in a real app, you'd load these from secure storage)
        access_token = input("Enter your access token (or press Enter to authenticate): ")
        refresh_token = input("Enter your refresh token (or press Enter to authenticate): ")
        
        if not access_token or not refresh_token:
            token = authenticate()
            access_token = token['access_token']
            refresh_token = token['refresh_token']

        client = Fitbit(CLIENT_ID, CLIENT_SECRET, oauth2=True, access_token=access_token, refresh_token=refresh_token)

        # Example: Get today's steps
        today = str(datetime.datetime.now().strftime("%Y-%m-%d"))
        try:
            steps = client.activities(date=today)['summary']['steps']
            print(f"Steps taken today: {steps}")
        except TokenExpiredError:
            # If token is expired, refresh it
            new_token = get_new_access_token(CLIENT_ID, CLIENT_SECRET, refresh_token)
            save_tokens(new_token)
            client = Fitbit(CLIENT_ID, CLIENT_SECRET, oauth2=True, access_token=new_token['access_token'], refresh_token=new_token['refresh_token'])
            steps = client.activities(date=today)['summary']['steps']
            print(f"Steps taken today: {steps}")

        # Example: Get sleep data for the past week
        end_date = datetime.datetime.now().date()
        start_date = end_date - datetime.timedelta(days=7)
        sleep_data = client.time_series('sleep', base_date=start_date, end_date=end_date)
        sleep_df = pd.DataFrame(sleep_data['sleep'])
        print(sleep_df)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
