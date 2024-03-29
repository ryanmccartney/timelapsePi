# Timelapse Pi

Python scripts using PiCamera, OpenCV and CherryPy leveraging the Raspberry Pi to create long term timelapses.

## Requirements

* `pip3 install cherrypy`
* `pip3 install opencv`
* `pip3 install glob`

## Installation Guide

1. `sudo apt-get update`
2. `git clone https://github.com/rmccartney856/timelapsePi`
3. `cd /PATH/timelapsePi/`
4. `sudo python3 install.py`
6. `sudo reboot`

## Usage

1. Install as described above.
2. Navigate to `http://HOSTNAME.local:8080` or `http://IPADDRESS.local:8080`
3. Adjust seetings, render and download timelapses.

## Screenshots

![Screenshot of Interface](https://github.com/rmccartney856/timelapsePi/blob/master/media/webScreenshot1.jpg)
![Screenshot of Interface](https://github.com/rmccartney856/timelapsePi/blob/master/media/webScreenshot2.jpg)

# Documentation

* FPS - Frames per second setting determines the number of photos that make up one second of a render video. Set as appropriate.
* Interval - Time between capturing photos in seconds.
* Start Time - The 24 hour time in the day which photo capture begins.
* Start Time - The 24 hour time in the day which photo capture stops.

# Further Work (In Progress)

* Start and Stop times determined dynamically based on sunset/sunrise time. Provision of longatude and latitude will be required.
* Live stream preview window rather than an image updated every 5 seconds.
* Responsive design
