#NAME:  start.py
#DATE:  Monday 15th July 2019
#AUTH:  Ryan McCartney
#DESC:  A python script for starting timelapsePi utility
#COPY:  Copyright 2019, All Rights Reserved, Ryan McCartney

import os

cwd = os.getcwd()

if __name__ == '__main__':
    
    print("Starting timelapsePi")
    cwd = os.getcwd()
    mainPath = cwd+"/main.py"
    os.system("sudo python3 "+mainPath)