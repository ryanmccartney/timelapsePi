#NAME:  install.py
#DATE:  Monday 15th July 2019
#AUTH:  Ryan McCartney
#DESC:  A python script for installing timelapsePi utility
#COPY:  Copyright 2019, All Rights Reserved, Ryan McCartney

import os

gitRepo = "https:github.com/rmccartney856/timelapsePi"
cwd = os.getcwd()

def getDependencies():
    #Install Dependencies
    os.system("sudo pip3 install --upgrade pip")
    os.system("sudo pip3 install CherryPy")
    os.system("sudo apt-get install python3-opencv")
    
def setupPythonStartup():
    
    startupFile = "/etc/rc.local"
    startupFileContents = None
    startCommand="sudo python3 "+str(cwd)+"/start.py"
        
    with open(startupFile, 'r') as file:
        startupFileContents = file.readlines()
    
    lineNumber = len(startupFileContents)-1
    startupFileContents.insert(lineNumber,startCommand + "\n")
    
    with open(startupFile,'w') as file:
        file.writelines(startupFileContents)
        
def changeHostname():
    #Change Hostname
    os.system("sudo hostname timelapse")

if __name__ == '__main__':
    
    print("Installing timelapsePi")
    cwd = os.getcwd()
    print("Getting Dependencies for Operation")
    getDependencies()
    print("Setting up Raspberry Pi to run timelapsePi on startup")
    setupPythonStartup()
    print("Adjusting Hostname to 'timelapse'")
    changeHostname()
    print("Installation complete. Please Reboot.")