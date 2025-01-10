# Fitbit API
This tool is designed to access the Fitbit API using the command line. It is currently built for Project PACE.

 ## Installation

### Step 1: Download Python
 If you don't have it already, you will need to download Python on your computer. You can download Python [here](https://www.python.org/downloads/). Keep in mind that a lot of computers come with Python pre-installed (the Rowan ones), so you may not need to download it.

 ### Step 2: Download or Clone the Repository
 The repository is pretty much what will be used in order to access the Fitbit API. You can download the repository by clicking the green "Code" button and then clicking "Download ZIP". 

 If you are familiar with Git and have Git installed on your computer, you can clone the repository by running the following command in your terminal or command prompt:
 
 ```bash
    git clone https://github.com/RajHarsor/Fitbit-API.git
```
After getting the zip file, you will need to extract the files from the zip file. You can do this by right-clicking the zip file and clicking "Extract All" or the equivalent on a Mac.

### Step 3: Install the Required Libraries
In order to use the Fitbit API, you will need to install the required libraries. You can do this by running the following command in your terminal or command prompt:

```
    pip install -r [path to requirements.txt in the repository]
```
### Step 4: Creating a .env file and adding the necessary information

In order to access the Fitbit API, you will need to obtain the proper path for the study_info.json and user_tokens.json files. In these files, there is information relevant to data accessing and processing. In order for all of us to access the data, this information will be stored on the google drive.

Since we need the path from google drive, we need to install the desktop version of google drive. You can download the desktop version of google drive [here](https://www.google.com/drive/download/). After downloading the desktop version of google drive, you will need to sign in with your Rowan email.

After signing in, in your file explorer, you will see a Google Drive folder. You will need to navigate to the proper folder in order to access the study_info.json and user_tokens.json files. The path to the folder should be something like this:

For Mac:
```
    '/Users/rajharsora/Library/CloudStorage/GoogleDrive-harsora@rowan.edu/Shared drives/Rowan CHASE Lab/5. Menstrual Cycle-PA (Salvatore LRP)/Fitbit API/user_tokens.json'
```
For Windows:
```

```
The paths for both of those files will be respectively put into the proper places in the .env file. The .env file will be provided on the Google Drive. You will need to download the .env file and place it in the Fitbit API folder. Following that, you will need to open the .env file and replace the placeholders with the proper paths (for info-path and tokens-path). Keep everything else the same (client ID, secret, etc.).

### Step 5: Custom Fitbit Library Installation
In order to access the Fitbit API and get all the information we needed, I made changes to an existing Fitbit API Package. The changes I made are in the file called 'api.py' which you can find in this repository. You will need to replace the 'api.py' file in the Fitbit API package with the one in this repository. You can find the Fitbit API package directory by typing in the following command in your command prompt/terminal:

```bash
    pip show fitbit
```
After running that command, you will see the location of the Fitbit API package. You will need to navigate to that location and replace the 'api.py' file with the one in this repository in "fitbit" folder.

### Step 6: Running the Program
After completing all the steps above, you can now run the program. You can do this by running the following command in your terminal or command prompt:

```bash
    python [path to main.py in the repository]
```