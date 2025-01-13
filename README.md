# Fitbit API
This tool is designed to access the Fitbit API using the command line. It is currently built for Project PACE.

**Current Version**: v1.0b

## Installation

### Step 1: Download Python
If you don't have it already, you will need to download Python on your computer. You can download Python [here](https://www.python.org/downloads/). It should be noted that Rowan computers cant download python, so you will need to login through Citrix Workspace to access the API. Python should be pre-installed on the Citrix workspace computers.

### Step 2: Download or Clone the Repository
The repository is what will be used in order to access the Fitbit API and the custom functions associated with the study and its needs. You can download the repository by clicking the green "Code" button and then clicking "Download ZIP" on this webpage.

*Alternatively*, if you are familiar with Git and have Git installed on your computer, you can clone (download) the repository by running the following command in your terminal (for mac) or command prompt (for windows):

```bash
git clone https://github.com/RajHarsor/Fitbit-API.git
```
After getting the zip file, you will need to extract the files from the zip. You can do this by right-clicking the zip file and clicking "Extract All..." or the equivalent on a Mac.

### Step 3: Installing the Required Libraries
In order to use the Fitbit API, you will need to install the required libraries. *Please note that you need to replace the "[path to requirements.txt in the repository]" part of the command with the actual path of the file.* This path can be found by navigating to the folder which you extracted the files to and finding the requirements.txt file. To get the path click on the file, then click "Home" on the top left of the file explorer, then click "Copy Path".

You can do this by running the following command in your terminal (for mac) or command prompt (for windows):

```bash
pip install -r [path to requirements.txt in the repository]
```
For windows the command may look something like this:
```bash
pip install -r C:\Users\rajha\Downloads\Fitbit-API-main\requirements.txt
```
### Step 4: Getting the .env file and adding the necessary information

In order to access the Fitbit API, you will need to obtain the proper path for the study_info.json and user_tokens.json files. In these files, there is information relevant to data accessing and processing. In order for all of us to access the data, this information will be stored on the google drive.

Since we need the path from google drive, we need to install the desktop version of google drive. You can download the desktop version of google drive [here](https://www.google.com/drive/download/). Citrix Workspace computers seem to already have them pre-installed so you can just type in "Google Drive" into windows search and it should come up. After downloading/accessing the desktop version of google drive, you will need to sign in with your Rowan email.

After signing in, in your file explorer, you will see a Google Drive folder. You will need to navigate to the proper folder in order to access the study_info.json and user_tokens.json files. The path to the folder should be something like this:

For Mac:
```
/Users/rajharsora/Library/CloudStorage/GoogleDrive-harsora@rowan.edu/Shared drives/Rowan CHASE Lab/5. Menstrual Cycle-PA (Salvatore LRP)/Fitbit API/user_tokens.json
```
For Windows:
```
C:\Shared drives\Rowan CHASE Lab\5. Menstrual Cycle-PA (Salvatore LRP)\Fitbit API\user_tokens.json
```
The paths for both of those files will be respectively put into the proper places in the .env file. The .env file will be provided on the Google Drive. You will need to download the .env file and place it in the Fitbit API folder that you extracted earlier. Following that, you will need to open the .env file using notepad and replace the placeholders with the proper paths (for info-path put the path for study_info.json and for tokens-path put the path to user_tokens.json). Keep everything else the same (client ID, secret, etc.). Please note that the path should **NOT** be in quotes.

### Step 5: Fitbit Library Modification
In order to access the Fitbit API and get all the information we need, I made changes to an existing Fitbit API Package. The changes I made are in the file called 'api.py' which you can find in this repository/files you downloaded and extracted. You will need to replace the 'api.py' file in the Fitbit API package with the one in this repository. You can find the Fitbit API package directory by typing in the following command in your command prompt/terminal:

```bash
pip show fitbit
```
After running that command, you will see the location of the Fitbit API package. You will need to navigate to that location, go to the "fitbit" folder and replace the 'api.py' file with the one in this repository. 

## Usage
After completing all the steps above, you can now run the program (you will never need to do the installation steps again unless changes are made). You can do this by running the following command in your terminal or command prompt:

```bash
python [path to project_pace_API.py in the repository]
```

Once again, you need to replace the "[path to project_pace_API.py in the repository]" part of the command with the actual path of the file. This path can be found by navigating to the folder which you extracted the files to and finding the project_pace_API.py file in the "Python" folder. To get the path click on the file, then click "Home" on the top left of the file explorer, then click "Copy Path". Paste that path into the command.

### Notes

The Fitbit API has a limit on the number of requests you can make in a certain amount of time. This limit is 150 requests per hour per user. This shouldn't be an issue for Project PACE but it is important to note. Documentation for rate limits can be found [here](https://community.fitbit.com/t5/Web-API-Development/How-do-API-rate-limits-work/td-p/324370).

## Supported Variables
