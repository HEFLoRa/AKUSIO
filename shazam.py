#!/usr/bin/python3
import os
os.chdir('/home/pi')
import time
import subprocess

#os.system("sudo /opt/vc/bin/tvservice -o")
#os.system("sudo sh -c 'echo 0 > /sys/class/leds/led1/brightness' ")
#os.system("sudo sh -c 'echo 0 > /sys/class/leds/led0/brightness' ")
#os.system("echo '1-1' |sudo tee /sys/bus/usb/drivers/usb/unbind")
print("Shazam Started!")
print("===============")
print("Starting Bird Voice Detection...")
print("===============")
subprocess.Popen(["python","/home/pi/Shazam4Nature-master-3/pi_main/main.py"])
print("LoRa Transmissions will start in 30 minutes...")
print("===============")
time.sleep(1800)
subprocess.Popen(["python","/home/pi/Shazam4Nature-master-3/pi_main/lmic-rpi-lora-gps-hat/examples/periodic/lora.py"])

