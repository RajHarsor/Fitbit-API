# Fitbit API
This tool is designed to access the Fitbit API using the command line. It is currently built for Project PACE.

**Current Version**: Version 2.1.3 (2025-07-24)

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


### Step 4: Fitbit Library Modification
In order to access the Fitbit API and get all the information we need, I made changes to an existing Fitbit API Package. The changes I made are in the file called 'api.py' which you can find in this repository/files you downloaded and extracted. You will need to replace the 'api.py' file in the Fitbit API package with the one in this repository. You can find the Fitbit API package directory by typing in the following command in your command prompt/terminal:

```bash
pip show fitbit
```
After running that command, you will see the location of the Fitbit API package. You will need to navigate to that location, go to the "fitbit" folder and replace the 'api.py' file with the one in this repository. 

## Usage
After completing all the steps above, you can now run the program (you will never need to do the installation steps again unless changes are made). You can do this by running the following command in your terminal or command prompt:

```bash
python -u [path to project_pace_API.py in the repository]
```

Once again, you need to replace the "[path to project_pace_API.py in the repository]" part of the command with the actual path of the file. This path can be found by navigating to the folder which you extracted the files to and finding the project_pace_API.py file in the "Python" folder. To get the path click on the file, then click "Home" on the top left of the file explorer, then click "Copy Path". Paste that path into the command.

### Notes

The Fitbit API has a limit on the number of requests you can make in a certain amount of time. This limit is 150 requests per hour per user. This shouldn't be an issue for Project PACE but it is important to note. Documentation for rate limits can be found [here](https://community.fitbit.com/t5/Web-API-Development/How-do-API-rate-limits-work/td-p/324370).

## Supported Variables

### Activity Data
- [Steps](https://dev.fitbit.com/build/reference/web-api/activity-timeseries/get-activity-timeseries-by-date-range/)
- [Activity Log List](https://dev.fitbit.com/build/reference/web-api/activity-timeseries/get-activity-timeseries-by-date-range/)
  - activeDuration
  - activityLevel
    - sedentary
    - lightly
    - fairly
    - very
  - activityName
  - activityTypeId
  - duration
  - lastModified
  - logId
  - logType
  - manualValuesSpecified
    - steps
  - originalDuration
  - originalStartTime
  - startTime
  - steps

### Sleep Data
[Link](https://dev.fitbit.com/build/reference/web-api/sleep/get-sleep-log-by-date-range/)
- dateOfSleep
- duration (ms)
- efficiency
- isMainSleep
- logType
- startTime