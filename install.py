#NAME:  install.py
#DATE:  Monday 15th July 2019
#AUTH:  Ryan McCartney
#DESC:  A python script for installing timelapsePi utility
#COPY:  Copyright 2019, All Rights Reserved, Ryan McCartney

import os
import json
gitRepo = "https:github.com/rmccartney856/timelapsePi"

def getDependencies():
    #Install Dependencies
    os.system("sudo pip3 install --upgrade pip")
    os.system("sudo pip3 install CherryPy")
    os.system("sudo apt-get install python3-opencv")
    
def setupPythonStartup():
    
    cwd = os.getcwd()
    startupFile = "/etc/rc.local"
    startupFileContents = None
    cdCommand ="cd "+str(cwd)
    startCommand="sudo python3 "+str(cwd)+"/start.py"
        
    with open(startupFile, 'r') as file:
        startupFileContents = file.readlines()
    
    lineNumber = len(startupFileContents)-1
    startupFileContents.insert(lineNumber,cdCommand + "\n")
    lineNumber = len(startupFileContents)-1
    startupFileContents.insert(lineNumber,startCommand + "\n")
    
    with open(startupFile,'w') as file:
        file.writelines(startupFileContents)
        
def changeHostname():
    #Change Hostname
    os.system("sudo hostname timelapse")

def addInstallDirectory():
    settingFilePath = "settings.json"
    cwd = os.getcwd()
    try:
        #Load Existing Settings
        settingsFile = open(settingFilePath,"r")
        settings = json.load(settingsFile)
        settingsFile.close()
        #Update Settings
        settings["path"] = cwd
        #Save Settings
        settingsFile = open(settingFilePath,"w")
        settingsFile.write(json.dumps(settings))
        settingsFile.close()
        print("INFO: Path updated.")
    except:
        print("ERROR: Path could not be updated.")
    
if __name__ == '__main__':
    
    print("INFO: Installing timelapsePi")
    addInstallDirectory()
    print("INFO: Getting Dependencies for Operation")
    getDependencies()
    print("INFO: Setting up Raspberry Pi to run timelapsePi on startup")
    setupPythonStartup()
    print("INFO: Adjusting Hostname to 'timelapse'")
    changeHostname()
    print("INFO: Installation complete. Please Reboot.")