import os
import json
import fitbit
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import boto3

# %%
class FitbitAuthSimple:
    def __init__(self):
        load_dotenv()
        
        ## Initialize Fitbit API credentials and file paths (Google Drive)
        self.client_id = os.getenv('FITBIT_CLIENT_ID')
        self.client_secret = os.getenv('FITBIT_CLIENT_SECRET')
        # Use a dummy redirect URI - Fitbit will still show the code
        self.redirect_uri = os.getenv('FITBIT_REDIRECT_URI')
        self.token_file = os.getenv('TOKENS_PATH')
        self.info_file = os.getenv('INFO_PATH')
        
        ## Initialize AWS credentials
        self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.aws_table_name = os.getenv('AWS_TABLE_NAME')
        self.region_name = "us-east-1"

    def get_auth_link(self):
        """Generate authorization link for a participant

        Returns:
            str: The authorization URL that the user should visit to authorize the application
        """
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
        """Save token using auth code from URL

        Args:
            user_id (str): The ID of the user
            auth_code (str): The authorization code received from Fitbit after user authorization

        Returns:
            dict: The access token and refresh token for the user
        """
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
        phone_number = input("Enter phone number (+1XXXXXXXXXX): ")
        morning_send_time = input("Enter morning send in MILITARY time (HH:MM): ")
        evening_send_time = input("Enter evening send time IN MILITARY time (HH:MM): ")

        # Save additional information
        self._save_user_info(user_id, wave_number, study_start_date, study_end_date, phone_number, morning_send_time, evening_send_time)
        
        # Send information to AWS dynamoDB
        
        Session = boto3.Session(
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.region_name
        )

        dynamodb = Session.resource("dynamodb")
        table = dynamodb.Table(self.aws_table_name)

        # Save user information to DynamoDB
        table.put_item(Item={
            'participant_id': user_id,
            'wave_number': wave_number,
            'study_start_date': study_start_date,
            'study_end_date': study_end_date,
            'phone_number': phone_number,
            'morning_send_time': morning_send_time,
            'evening_send_time': evening_send_time
        })
        print(f"User {user_id} authorized and information saved.")
        return tokens

    def _save_tokens(self, user_id, tokens):
        """Save access and refresh tokens for a user to JSON

        Args:
            user_id (str): The ID of the user
            tokens (dict): The access token and refresh token for the user
        """
        all_tokens = self._load_all_tokens()
        all_tokens[user_id] = tokens
        with open(self.token_file, 'w') as f:
            json.dump(all_tokens, f)

    def _load_all_tokens(self):
        """Load all access and refresh tokens from JSON

        Returns:
            dict: A dictionary of user IDs and their corresponding tokens
        """
        try:
            with open(self.token_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def _load_all_info(self):
        """Load all user information from JSON

        Returns:
            dict: A dictionary of user IDs and their corresponding information
        """
        try:
            with open(self.info_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}

    def _save_user_info(self, user_id, wave_number, study_start_date, study_end_date, phone_number, morning_send_time, evening_send_time):
        """Save user information to JSON

        Args:
            user_id (str): The ID of the user
            wave_number (str): The wave number
            study_start_date (str): The study start date
            study_end_date (str): The study end date
        """
        all_info = self._load_all_info()
        all_info[user_id] = {
            'wave_number': wave_number,
            'study_start_date': study_start_date,
            'study_end_date': study_end_date,
            'phone_number': phone_number,
            'morning_send_time': morning_send_time,
            'evening_send_time': evening_send_time
        }
        with open(self.info_file, 'w') as f:
            json.dump(all_info, f)
    
    def delete_user(self, user_id):
        """Delete user from both JSON files

        Args:
            user_id (str): The ID of the user
        """
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
        """Get steps data for a user between two dates

        Args:
            user_id (str): The ID of the user
            start_date (str): The start date in 'YYYY-MM-DD' format
            end_date (str, optional): The end date in 'YYYY-MM-DD' format. Defaults to None, which means the last 1 day will be used.

        Raises:
            ValueError: If no tokens are found for the user

        Returns:
            dict: Steps data for the user between the specified dates
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
        """Extract steps data for all users between two dates

        Args:
            json_file_path (str): The path to the JSON file containing user data
            start_date (str): The start date in 'YYYY-MM-DD' format
            end_date (str): The end date in 'YYYY-MM-DD' format
        
        Returns:
            pd.DataFrame: A DataFrame containing steps data for all users between the specified dates
        
        Raises:
            FileNotFoundError: If the JSON file does not exist
        """
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

        """Extract steps data for all users according to the study period defined in the info file

        Returns:
            pd.DataFrame: A DataFrame containing steps data for all users according to the study period
        """

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
        """Extract sleep data for all users according to the study period defined in the info file
        
        Returns:
            pd.DataFrame: A DataFrame containing sleep data for all users according to the study period
        """
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
                        startTime = None
                    else:
                        duration = day['duration']
                        efficiency = day['efficiency']
                        is_main_sleep = day.get('isMainSleep', None)
                        logType = day.get('logType', None)
                        startTime = day.get('startTime', None)
                    all_data.append({
                        'user_id': user_id,
                        'wave_number': user_data['wave_number'],
                        'date': day['dateOfSleep'],
                        'duration (ms)': duration,
                        'efficiency': efficiency,
                        'is_main_sleep': is_main_sleep,
                        'log_type': logType,
                        'start_time': startTime
                    })
                    # Debug print
                    print(f"User: {user_id}, Date: {day['dateOfSleep']}, Duration: {duration}, Efficiency: {efficiency}, isMainSleep: {is_main_sleep}, logType: {logType}, startTime: {startTime}")
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
        """Extract activity data for all users according to the study period defined in the info file

        Returns:
            pd.DataFrame: A DataFrame containing activity data for all users according to the study period
        """

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
            # Go through each row and see if the date is outside the study period for that user. If it is, delete the row.
            for index, row in df.iterrows():
                user_id = row['user_id']
                user_data = all_users_data[user_id]
                date = datetime.strptime(row['date'], '%Y-%m-%d')
                if date < datetime.strptime(user_data['study_start_date'], '%Y-%m-%d') or date > datetime.strptime(user_data['study_end_date'], '%Y-%m-%d'):
                    df.drop(index, inplace=True)

            output_file = f'activity_data_study_period.csv'
            df.to_csv(output_file, index=False)
            print(f"Data exported to {output_file}")
            print(all_data)
            return df
        else:
            print("No data found for the specified date range")
            return None


"""NEW METHODS FOR V2.0"""

def check_env_file_exists() -> bool:
    """Check if the .env file exists in the current directory

    Returns:
        bool: True if the .env file exists, False otherwise
    """
    load_dotenv()
    return os.path.exists('.env')

def check_env_variables() -> tuple[bool, str]:
    """Check if all required environment variables are set

    Returns:
        tuple[bool, str]: A tuple containing a boolean indicating if all variables are set,
                          and a string with the names of any missing variables
    """
    current_dir = os.getcwd()
    env_file_path = os.path.join(current_dir, '.env')
    
    # Read the .env file firectly to check for variables
    env_vars = {}
    try:
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    except Exception as e:
        return False, f"Error reading .env file: {e}"
    
    required_vars = [
        'FITBIT_CLIENT_ID',
        'FITBIT_CLIENT_SECRET',
        'FITBIT_CALLBACK_URL',
        'TOKENS_PATH',
        'INFO_PATH',
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'AWS_REGION',
        'AWS_TABLE_NAME'
    ]
    
    missing_vars = []
    for var in required_vars:
        if var not in env_vars or not env_vars[var]:
            missing_vars.append(var)
    
    if missing_vars:
        return False, f"{', '.join(missing_vars)}"
    else:
        return True, "All required environment variables are set."

def create_env_file(fitbit_client_id: str,
                    fitbit_client_secret: str,
                    tokens_path: str,
                    info_path: str,
                    aws_access_key_id: str,
                    aws_secret_access_key: str):
    """Create a .env file with the provided environment variables

    Args:
        fitbit_client_id (str): Fitbit client ID
        fitbit_client_secret (str): Fitbit client secret
        tokens_path (str): Path to the tokens JSON file
        info_path (str): Path to the user info JSON file
        aws_access_key_id (str): AWS access key ID
        aws_secret_access_key (str): AWS secret access key
        
    Returns:
        None
    """
    with open('.env', 'w') as f:
        f.write(f"FITBIT_CLIENT_ID={fitbit_client_id}\n")
        f.write(f"FITBIT_CLIENT_SECRET={fitbit_client_secret}\n")
        f.write(f"FITBIT_CALLBACK_URL=https://drarigo.wordpress.com\n")
        f.write(f"TOKENS_PATH={tokens_path}\n")
        f.write(f"INFO_PATH={info_path}\n")
        f.write(f"AWS_ACCESS_KEY_ID={aws_access_key_id}\n")
        f.write(f"AWS_SECRET_ACCESS_KEY={aws_secret_access_key}\n")
        f.write(f"AWS_REGION=us-east-1\n")
        f.write(f"AWS_TABLE_NAME=PACE_Participants\n")

def update_env_file():
    """Updates one of the .env file with new environment variables

    Returns:
        None
    """
    # Make the user choose which variable to update
    print("Which environment variable would you like to update?")
    print("1. FITBIT_CLIENT_ID\n2. FITBIT_CLIENT_SECRET\n3. TOKENS_PATH\n4. INFO_PATH\n5. AWS_ACCESS_KEY_ID\n6. AWS_SECRET_ACCESS_KEY\n7. AWS_REGION\n8. AWS_TABLE_NAME")

    choice = input("Enter the number of your choice: ")
    env_var_name = ""
    match choice:
        case "1":
            env_var_name = "FITBIT_CLIENT_ID"
        case "2":
            env_var_name = "FITBIT_CLIENT_SECRET"
        case "3":
            env_var_name = "TOKENS_PATH"
        case "4":
            env_var_name = "INFO_PATH"
        case "5":
            env_var_name = "AWS_ACCESS_KEY_ID"
        case "6":
            env_var_name = "AWS_SECRET_ACCESS_KEY"
        case "7":
            env_var_name = "AWS_REGION"
        case "8":
            env_var_name = "AWS_TABLE_NAME"
        case _:
            print("Invalid choice")
            return

    new_value = input(f"Enter the new value for {env_var_name}: ")

    # Update the .env file
    current_dir = os.getcwd()
    env_file_path = os.path.join(current_dir, '.env')

    try:
        with open(env_file_path, 'r') as f:
            lines = f.readlines()
        with open(env_file_path, 'w') as f:
            for line in lines:
                if line.startswith(env_var_name):
                    f.write(f"{env_var_name}={new_value}\n")
                else:
                    f.write(line)
    except Exception as e:
        print(f"Error updating .env file: {e}")

def send_test_message():
    """Send a test message to the specified phone number using AWS SNS
    Args:
        phone_number (str): The phone number to send the message to
        message (str): The message to send

    Returns:
        None
    """
    user_id = input("Enter the participant ID you want to send a message to: ")
    message = input("Enter the message you want to send: ")

    # Initialize dynamoDB client
    Session = boto3.Session(
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION')
    )
    
    dynamodb = Session.resource("dynamodb")
    table = dynamodb.Table(os.getenv('AWS_TABLE_NAME'))
    
    # Get the user's phone number from the DynamoDB table
    response = table.get_item(Key={'participant_id': user_id})
    # Print the phone number
    if 'Item' in response:
        print(f"Sending message to user {user_id} with phone number {response['Item']['phone_number']}")
    if 'Item' not in response:
        print(f"No user found with ID {user_id}")
        return
    
    sns = Session.client('sns')

    # Send the test message
    sns.publish(
        PhoneNumber=response['Item']['phone_number'],
        Message=message
    )