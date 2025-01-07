# Fitbit API
This tool is designed to access the Fitbit API using the command line. It is currently built for Project PACE.

 ## Installation

For non-technical people, there are quite a few steps but hopefully this guide will help.

### Step 1: Download Python
 If you don't have it already, you will need to download Python on your computer. You can download Python [here](https://www.python.org/downloads/). Keep in mind that a lot of computers come with Python pre-installed (the Rowan ones), so you may not need to download it.

 ### Step 2: Download or Clone the Repository
 The repository is pretty much what will be used in order to access the Fitbit API. You can download the repository by clicking the green "Code" button and then clicking "Download ZIP". 

 If you are familiar with Git and have Git installed on your computer, you can clone the repository by running the following command in your terminal:
 
 ```bash
    git clone https://github.com/RajHarsor/Fitbit-API.git
```
After getting the zip file, you will need to extract the files from the zip file. You can do this by right-clicking the zip file and clicking "Extract All".

### Step 3: Install the Required Libraries
In order to use the Fitbit API, you will need to install the required libraries. You can do this by running the following command in your command prompt:

```
    pip install -r [path to requirements.txt in the repository]
```
### Step 4: Linking the proper study_info.json and user_tokens.json files

In order to access the Fitbit API, you will need to obtain the proper path for the study_info.json and user_tokens.json files. In these files, there is information relevant to data accessing and processing. In order for all of us to access the data, this information will be stored on the google drive.

Since we need the path from google drive, we need to install the desktop version of google drive. You can download the desktop version of google drive [here](https://www.google.com/drive/download/). After downloading the desktop version of google drive, you will need to sign in with your Rowan email.

After signing in, in your file explorer, you will see a Google Drive folder. You will need to navigate to the proper folder in order to access the study_info.json and user_tokens.json files. The path to the folder should be something like this:

TODO: Add path to folder
```
    C:\Users\[Your Username]\Google Drive\PACE\PACE-Data\fitbit
```
