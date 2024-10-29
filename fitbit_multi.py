import fitbit
from fitbit.api import Fitbit
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError
from requests_oauthlib import OAuth2Session
import datetime
import pandas as pd
import sqlite3
from flask import Flask, request, redirect
import threading
import uuid

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

# Flask app for handling callbacks
app = Flask(__name__)

# Database setup
def setup_db():
    conn = sqlite3.connect('fitbit_users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id TEXT PRIMARY KEY, access_token TEXT, refresh_token TEXT)''')
    conn.commit()
    conn.close()

def save_tokens(user_id, access_token, refresh_token):
    conn = sqlite3.connect('fitbit_users.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users VALUES (?, ?, ?)", 
              (user_id, access_token, refresh_token))
    conn.commit()
    conn.close()

def get_tokens(user_id):
    conn = sqlite3.connect('fitbit_users.db')
    c = conn.cursor()
    c.execute("SELECT access_token, refresh_token FROM users WHERE id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result if result else (None, None)

def get_new_access_token(user_id):
    access_token, refresh_token = get_tokens(user_id)
    if not refresh_token:
        return None
    
    oauth = OAuth2Session(client_id=CLIENT_ID, token={'refresh_token': refresh_token})
    new_token = oauth.refresh_token(TOKEN_URL, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    save_tokens(user_id, new_token['access_token'], new_token['refresh_token'])
    return new_token['access_token']

def generate_auth_url():
    oauth = OAuth2Session(CLIENT_ID, redirect_uri=CALLBACK_URL, scope=SCOPES)
    authorization_url, _ = oauth.authorization_url(AUTH_URL)
    return authorization_url

@app.route('/callback')
def callback():
    user_id = request.args.get('state')
    oauth = OAuth2Session(CLIENT_ID, redirect_uri=CALLBACK_URL)
    token = oauth.fetch_token(TOKEN_URL, client_secret=CLIENT_SECRET,
                              authorization_response=request.url)
    save_tokens(user_id, token['access_token'], token['refresh_token'])
    return f"Authorization successful for user {user_id}. You can close this window."

def start_flask():
    app.run(port=8080)

def get_user_data(user_id):
    access_token, refresh_token = get_tokens(user_id)
    if not access_token:
        print(f"No tokens found for user {user_id}")
        return

    client = Fitbit(CLIENT_ID, CLIENT_SECRET, oauth2=True, access_token=access_token, refresh_token=refresh_token)

    try:
        # Get today's steps
        today = str(datetime.datetime.now().strftime("%Y-%m-%d"))
        steps = client.activities(date=today)['summary']['steps']
        print(f"Steps taken today by user {user_id}: {steps}")

        # Get sleep data for the past week
        end_date = datetime.datetime.now().date()
        start_date = end_date - datetime.timedelta(days=7)
        sleep_data = client.time_series('sleep', base_date=start_date, end_date=end_date)
        sleep_df = pd.DataFrame(sleep_data['sleep'])
        print(f"Sleep data for user {user_id}:")
        print(sleep_df)

    except TokenExpiredError:
        # If token is expired, refresh it
        new_access_token = get_new_access_token(user_id)
        if new_access_token:
            client = Fitbit(CLIENT_ID, CLIENT_SECRET, oauth2=True, access_token=new_access_token, refresh_token=refresh_token)
            # Retry the data fetch (you might want to implement this more elegantly)
            get_user_data(user_id)
        else:
            print(f"Failed to refresh token for user {user_id}")

def main():
    setup_db()
    
    # Start Flask in a separate thread
    threading.Thread(target=start_flask, daemon=True).start()

    while True:
        print("\n1. Add new user")
        print("2. Get user data")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            user_id = str(uuid.uuid4())  # Generate a unique user ID
            auth_url = generate_auth_url()
            print(f"Send this authorization URL to the user (ID: {user_id}):")
            print(auth_url + f"&state={user_id}")
        elif choice == '2':
            user_id = input("Enter user ID: ")
            get_user_data(user_id)
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()