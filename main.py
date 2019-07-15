#NAME:  main.py
#DATE:  Friday 12th July 2019
#AUTH:  Ryan McCartney
#DESC:  A python script for using the rpi camera to create timelapses via a web interface
#COPY:  Copyright 2019, All Rights Reserved, Ryan McCartney

from picamera import PiCamera
from io import BytesIO
import threading
import cherrypy
from cherrypy.lib import file_generator
from cherrypy.lib import static
import cv2 as cv
import datetime
import time
import json
import glob
import os

#define threading wrapper
def threaded(fn):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper

try:
    class API(object):
       
        cameraConnected = False
        logFilePath = "public/log.txt"
        settingsPath = "settings.json"
        logging = True
        
        def __init__(self):
            
            #Get Directory Info
            localDir = os.path.dirname(__file__)
            self.absPath = os.path.join(os.getcwd(), localDir)
            self.log("System starting up...",1)

            #Current Frame Position
            self.frame = 0
            self.rendering = False
                       
            #Setting Parameters
            self.nightMode = False
            self.fps = 20
            self.rotation = 180
            self.interval = 120
            self.logging = True
            
            #Begin on Start
            self.loadSettings()
            self.timelapsing = True
            self.startTimelapse()
            
        @cherrypy.expose
        def index(self):
            #On index try to connect camera
            self.startCamera()
            with open ("index.html", "r") as webPage:
                contents=webPage.readlines()
            return contents
    
        @cherrypy.expose
        def startRender(self):
            if not self.rendering:
                status = "Starting Timelapse Render."
                self.render()
            else:
                status = "Already rendering a timelapse, wait until the render is finished."
            self.log(status,1)
            return status
        
        @threaded
        def render(self):
            if not self.rendering:
                self.rendering = True
                try:
                    currentDateTime = time.strftime("%d-%m-%Y %H-%M-%S")
                    filename = "renders/"+currentDateTime+".avi"
                
                    #Define the codec and create VideoWriter object
                    fourcc = cv.VideoWriter_fourcc(*'XVID')
                    out = cv.VideoWriter(filename,fourcc,self.fps,(2592,1944))
                
                    path = 'frames/*'
                    files = sorted(glob.glob(path))
                    for file in files:
                        #Load Frame
                        frame = cv.imread(file)
                        #Write the Frame
                        out.write(frame)
                    
                    #Release the frame
                    out.release()
                    self.log("Render Succesful.",1)
                except:
                    self.log("Rendering Failed.",0)
                self.rendering = False
                 
        @cherrypy.expose
        def startTimelapse(self):
            status = "Starting Timelapse"
            self.timelapsing = True
            self.captureImages()
            self.log(status,1)
            return status
            
        @cherrypy.expose
        def stopTimelapse(self):
            status = "Stopping Timelapse"
            self.timelapsing = False
            self.log(status,1)
            return status
        
        @cherrypy.expose
        def download(self):
            status = "Download starting..."
            self.log(status,1)
            
            path = 'renders/*'
            files = glob.glob(path)
            files.sort(key=os.path.getmtime,reverse=True)
            
            fullPath = self.absPath + files[0]
            return static.serve_file(fullPath)
        
        @cherrypy.expose
        def clearFrames(self):
            path = 'frames/*'
            files = glob.glob(path)
            for file in files:
               os.remove(file)
            
            status = "Deleted "+str(len(files))+" frames from disk."
            self.frame = 0
            self.log(status,1)
            self.saveSettings()
            return status
        
        @cherrypy.expose
        def rotate(self):
            if (self.rotation+90) >= 360:
                self.rotation = 0
            else:
                 self.rotation += 90
            self.camera.rotation = self.rotation
            status = "Image rotated to "+str(self.rotation)+" degrees."
            self.log(status,1)
            return status
                 
        def startCamera(self):
            if not self.cameraConnected:
                try:
                    self.camera = PiCamera()
                    self.camera.resolution = (2592,1944)
                    self.camera.rotation = self.rotation
                    self.camera.start_preview()
                    self.cameraConnected = True
                    self.log("Camera connected.",1)
                except:
                    self.cameraConnected = False
                    self.log("Camera not connected",0)

        @threaded
        def captureImages(self):     
            self.startCamera()
            self.updateTiming(self.startTime,self.endTime)
            nextCapture = time.time()
            while self.timelapsing:
                if ((self.startTimeSeconds < time.time())and(time.time()<self.endTimeSeconds)) or self.nightMode:
                    if time.time() > nextCapture:
                        succesfulCapture = False
                        while not succesfulCapture:
                            try:
                                imageName = "frames/"+str(self.frame).zfill(5)+".jpg"                        
                                self.camera.capture(imageName)
                                #Log as sucessful
                                self.log("Succefully captured frame number "+str(self.frame)+".",1)
                                succesfulCapture = True
                                self.frame += 1
                                self.saveSettings()
                            except:
                                self.log("Failed to capture frame number "+str(self.frame)+".",0)
                                self.startCamera()
                                time.sleep(1)
                        #Calculate the time to next photo
                        nextCapture = time.time()+self.interval
                    time.sleep(1)
                else:
                    time.sleep(300)
                    self.updateTiming(self.startTime,self.endTime)
     
        @cherrypy.expose
        def updateSettings(self,fps,interval,startTime,endTime):
            status = "Parameters for timelapse updated successfully."
            fps = int(fps)
            interval = int(interval)
            if fps > 0:
                self.fps = fps
                self.log(status,1)
            else:
                status = "Invalid frames per second value."
                self.log(status,0)
                
            if interval > 0:
                self.interval = interval
            else:
                status = "Invalid interval value."
                self.log(status,0)
            
            self.updateTiming(startTime,endTime)
            self.saveSettings()
            return status
        
        def updateTiming(self,startTime,endTime):
            
            try:
                now = datetime.datetime.now()
                todayBegin = int(datetime.datetime(now.year, now.month, now.day, 0, 0).strftime('%s'))
             
                #Start Time Calculation
                time = startTime.split(':')
                time = list(map(int, time))
                seconds = (time[0]*3600)+(time[1]*60)
                self.startTimeSeconds = todayBegin + seconds
            
                #End Time Calculation
                time = endTime.split(':')
                time = list(map(int, time))
                seconds = time[0]*3600+time[1]*60
                self.endTimeSeconds = todayBegin + seconds
            
                #Save Values
                self.startTime = startTime
                self.endTime = endTime
            
            except:
                self.log("Could not calculate timings",0)
            
        def saveSettings(self):
            try:
                #Load Existing Settings
                settingsFile = open(self.settingsPath,"r")
                settings = json.load(settingsFile)
                settingsFile.close()
                
                #Update Settings
                settings["fps"] = self.fps
                settings["interval"] = self.interval
                settings["frame"] = self.frame
                settings["startTime"] = self.startTime
                settings["endTime"] = self.endTime
                settings["rotation"] = self.rotation
                settings["logging"] = self.logging
                
                #Load Existing Settings
                settingsFile = open(self.settingsPath,"w")
                settingsFile.write(json.dumps(settings))
                settingsFile.close()
                
                self.log("Settings saved.",1)
            except:
                self.log("Settings could not be saved",0)
        
        @cherrypy.expose
        def getSettings(self):
            settings = str(self.fps)+","+str(self.interval)+","+str(self.startTime)+","+str(self.endTime)
            return settings
        
        def loadSettings(self):
            try:
                with open(self.settingsPath) as settingsFile:  
                    settings = json.load(settingsFile)
                    self.fps  = settings["fps"]
                    self.interval  = settings["interval"]
                    self.frame  = settings["frame"]
                    self.startTime  = settings["startTime"]
                    self.endTime  = settings["endTime"]
                    self.rotation = settings["rotation"]
                    self.logging = settings["logging"]
                self.log("Settings loaded.",1)
            except:
                self.log("Settings could not be loaded",0)
           
        @cherrypy.expose
        def getImage(self):
            cherrypy.response.headers['Content-Type'] = "image/jpeg"
            self.startCamera()
            stream = BytesIO()
            #stream = StringIO.StringIO()
            try:
                self.camera.capture(stream, format='jpeg')
                stream.seek(0)
            except:
                self.log("Could not get an image from camera.",0)
            
            return file_generator(stream)
        
        @cherrypy.expose
        def getStatus(self):
            return self.status
            
        @cherrypy.expose
        def getCPUTemp(self):
            res = os.popen('vcgencmd measure_temp').readline()
            return(res.replace("temp=","").replace("'C\n",""))
        
        @cherrypy.expose
        def getCPUUse(self):
            CPUUsage = str(os.popen("top -d 0.5 -b -n2 | grep 'Cpu(s)'|tail -n 1 | awk '{print $2 + $4}'").readline().strip())
            return CPUUsage
      
        @cherrypy.expose
        def getDiskRemaining(self):
            p = os.popen("df -h /")
            for i in range(0,2):
                 value = p.readline().split()[1:5]
                 diskRemain = value[2].replace("G","")
            return diskRemain
        
        @cherrypy.expose
        def getDiskUse(self):
            p = os.popen("df -h /")
            for i in range(0,2): 
                 value = p.readline().split()[1:5]
                 diskUse = value[3].replace("%","")
            return diskUse
        
        @cherrypy.expose
        def clearLogs(self):
            status = "Log file cleared"
            logFile = open(self.logFilePath,"w")
            logFile.write("Date,Time,Type,Entry\n")
            logFile.close()
            self.log(status,1)
            return status
      
        def log(self,message,indicator):
            message = str(message)
            self.status = message
            if self.logging:
                if indicator == 0:
                    message = "ERROR,"+message
                if indicator == 1:
                    message = "INFO,"+message
                currentDateTime = time.strftime("%d/%m/%Y,%H:%M:%S,")
                logEntry = currentDateTime + str(message)
                #open a txt file to use for logging
                logFile = open(self.logFilePath,"a+")
                logFile.write(logEntry+"\n")
                logFile.close()
                #Print Message to Terminal
                print(logEntry)     

    if __name__ == '__main__':

        cherrypy.config.update(
            {'server.socket_host': '0.0.0.0'}
        )     
        cherrypy.quickstart(API(), '/',
            {
                'favicon.ico':{
                    'tools.staticfile.on': True,
                    'tools.staticfile.filename': os.path.join(os.getcwd(),'public/favicon.ico')
                },
                '/public':{
                    'tools.staticdir.on'    : True,
                    'tools.staticdir.dir'   : os.path.join(os.getcwd(),'public'),
                    'tools.staticdir.index' : 'index.html',
                    'tools.gzip.on'         : True
                }
            }
        )        
except:
    print("ERROR: Main sequence error.")
