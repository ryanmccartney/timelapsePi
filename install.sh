echo "Installing Timelapse Pi"
#
#Acquire Dependencies
#sudo pip3 install --upgrade pip
#sudo pip3 install CherryPy
#sudo apt-get install python3-opencv
#
#Setting up start up scripts
sudo chmod +x "start.sh"
startCommand="sudo bash $PWD/start.sh"
echo "$startCommand"

sed -e '$i \$startCommand\n' /etc/rc.local
#sudo echo "$startCommand" >> /etc/rc.local
echo "Timelapse startup script setup"
#
#Change Hostname
echo "Change hostname to 'timelapse'"
sudo hostname timelapse
#
#Request Restart
echo "Installing Complete. Reboot your Pi."