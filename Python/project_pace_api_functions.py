import os
import json
import fitbit
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

# %%
class FitbitAuthSimple:
    def __init__(self):
        load_dotenv()
        self.client_id = os.getenv('FITBIT_CLIENT_ID')
        self.client_secret = os.getenv('FITBIT_CLIENT_SECRET')
        # Use a dummy redirect URI - Fitbit will still show the code
        self.redirect_uri = os.getenv('FITBIT_REDIRECT_URI')
        # TODO: Need to change the JSON file locations to Google Drive so everyone can access
        self.token_file = 'user_tokens.json'
        self.info_file = 'study_info.json'

    def get_auth_link(self, user_id):
        """Generate authorization link for a participant"""
        client = fitbit.Fitbit(
            self.client_id,
            self.client_secret,
            redirect_uri=self.redirect_uri,
            oauth2=True
        )
        url, _ = client.client.authorize_token_url(
            scope=['activity', 'sleep']
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

        # Prompt for additional information
        wave_number = input("Enter wave number: ")
        study_start_date = input("Enter study start date (YYYY-MM-DD): ")
        study_end_date = input("Enter study end date (YYYY-MM-DD): ")

        # Save additional information
        self._save_user_info(user_id, wave_number, study_start_date, study_end_date)

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

    def _load_all_info(self):
        try:
            with open(self.info_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}

    def _save_user_info(self, user_id, wave_number, study_start_date, study_end_date):
        all_info = self._load_all_info()
        all_info[user_id] = {
            'wave_number': wave_number,
            'study_start_date': study_start_date,
            'study_end_date': study_end_date
        }
        with open(self.info_file, 'w') as f:
            json.dump(all_info, f)
    
    def delete_user(self, user_id):
        """Delete user from both JSON files"""
        # Load tokens and info
        all_tokens = self._load_all_tokens()
        all_info = self._load_all_info()

        # Remove user if exists
        if user_id in all_tokens:
            del all_tokens[user_id]
            with open(self.token_file, 'w') as f:
                json.dump(all_tokens, f)
            print(f"Deleted user {user_id} from tokens file.")
        else:
            print(f"User {user_id} not found in tokens file.")

        if user_id in all_info:
            del all_info[user_id]
            with open(self.info_file, 'w') as f:
                json.dump(all_info, f)
            print(f"Deleted user {user_id} from info file.")
        else:
            print(f"User {user_id} not found in info file.")

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
        """Extract steps data for all users between dates"""
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

    def extract_all_users_steps_study_period(self):
        """Extract steps data for all users according to the study period"""
        # Read JSON file
        with open(self.info_file, 'r') as file:
            all_users_data = json.load(file)

        # Lists to store data
        all_data = []

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
                steps_data = client.time_series('activities/steps', base_date=user_data['study_start_date'], end_date=user_data['study_end_date'])
                for day in steps_data['activities-steps']:
                    date = datetime.strptime(day['dateTime'], '%Y-%m-%d')
                    if date > datetime.now():
                        steps = float('nan')
                    else:
                        steps = int(day['value'])
                    all_data.append({
                        'user_id': user_id,
                        'wave_number': user_data['wave_number'],
                        'date': day['dateTime'],
                        'steps': steps
                    })
                    # Debug print
                    print(f"User: {user_id}, Date: {day['dateTime']}, Steps: {day['value']}")
            except Exception as e:
                print(f"Error retrieving data for user {user_id}: {e}")

        # Create DataFrame
        if all_data:
            df = pd.DataFrame(all_data)
            df['steps'] = df['steps'].astype(float)
            output_file = f'steps_data_study_period.csv'
            df.to_csv(output_file, index=False)
            print(f"Data exported to {output_file}")
            return df
        else:
            print("No data found for the specified date range")
            return None

    def extract_all_users_sleepData_study_period(self):
        """Extract sleep data for all users according to the study period"""
        # Read JSON file
        with open(self.info_file, 'r') as file:
            all_users_data = json.load(file)

        # Lists to store data
        all_data = []

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
                sleep_data = client.time_series('sleep', base_date=user_data['study_start_date'], end_date=user_data['study_end_date'])
                # Save all sleep data as a JSON file
                #with open(f'sleep_data_{user_id}.json', 'w') as f:
                    #json.dump(sleep_data, f)
                for day in sleep_data['sleep']:
                    date = datetime.strptime(day['dateOfSleep'], '%Y-%m-%d')
                    if date > datetime.now():
                        duration = float('nan')
                        efficiency = float('nan')
                        is_main_sleep = None
                        logType = None
                    else:
                        duration = day['duration']
                        efficiency = day['efficiency']
                        is_main_sleep = day.get('isMainSleep', None)
                        logType = day.get('logType', None)
                    all_data.append({
                        'user_id': user_id,
                        'wave_number': user_data['wave_number'],
                        'date': day['dateOfSleep'],
                        'duration (ms)': duration,
                        'efficiency': efficiency,
                        'is_main_sleep': is_main_sleep,
                        'log_type': logType
                    })
                    # Debug print
                    print(f"User: {user_id}, Date: {day['dateOfSleep']}, Duration: {duration}, Efficiency: {efficiency}, isMainSleep: {is_main_sleep}, logType: {logType}")
            except Exception as e:
                print(f"Error retrieving data for user {user_id}: {e}")

        # Create DataFrame
        if all_data:
            df = pd.DataFrame(all_data)
            df['duration (ms)'] = df['duration (ms)'].astype(float)
            # Convert duration from ms to mins
            df['duration (mins)'] = df['duration (ms)'] / 60000
            df['efficiency'] = df['efficiency'].astype(float)
            output_file = f'sleep_data_study_period.csv'
            df.to_csv(output_file, index=False)
            print(f"Data exported to {output_file}")
            return df

    def extract_all_users_activity_study_period(self):
        """Extract activity data for all users according to the study period"""
        # Read JSON file
        with open(self.info_file, 'r') as file:
            all_users_data = json.load(file)

        # Lists to store data
        all_data = []

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
                """Get activity list for a user between dates"""
                #Get activity data:
                activity_data = client.activity_PACE_loglist(afterDate=user_data['study_start_date'])
                
                # Organize data
                rows = []
                for activities in activity_data["activities"]:
                    row = {
                        'user_id': user_id,
                        'date': activities['startTime'].split('T')[0],
                        'activityName': activities['activityName'],
                        'activityTypeId': activities['activityTypeId'],
                        'duration (ms)': activities['duration'],
                        'duration (mins)': activities['duration'] / 60000,
                        'originalDuration (ms)': activities['originalDuration'],
                        'originalDuration (mins)': activities['originalDuration'] / 60000,
                        'logType': activities['logType'],
                        'manualValuesSpecified_steps': activities['manualValuesSpecified']['steps'],
                        'startTime': activities['startTime'],
                        'originalDuration': activities['originalDuration'],
                        'lastModified': activities['lastModified']
                    }
                    # Add activity levels as separate columns
                    for level in activities['activityLevel']:
                        row[level['name']] = level['minutes']
                    rows.append(row)
                all_data.extend(rows)
            except Exception as e:
                print(f"Error retrieving data for user {user_id}: {e}")
            
        # Create DataFrame
        if all_data:
            df = pd.DataFrame(all_data)
            output_file = f'activity_data_study_period.csv'
            df.to_csv(output_file, index=False)
            print(f"Data exported to {output_file}")
            print(all_data)
            return df
        else:
            print("No data found for the specified date range")
            return None