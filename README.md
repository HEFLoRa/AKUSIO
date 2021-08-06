# AKUSIO

## 1)	Raspberry Pi setup
   ### Step 1: Install Raspberry Pi OS Lite on a microSD card.
   ### Step 2: Use a keyboard and a monitor to connect the RPI over WiFi for easier access over VNC or Teamviewer. 
   ### Step 3: Install required libraries:
   - Python3
   -	Pip3
   -	Numpy
   -	Scipy
   -	Deltasigma
   -	Tensorflow
   -	Keras
   -	Webrtcvad
   -	Librosa
   -	ReSpeaker Voice card

The previous steps are in case of setting up the RPi from scratch, please follow the Required Libraries section for faster installation of the required libraries, or simply write the Shazam.img file directly to the MicroSD card and mount it in the RPi.

## 2)	Required Libraries 
     1)	Make python3 the default python:
            update-alternatives --list python
            sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.7 1
     2)	Install pip:
            sudo apt update
            sudo apt upgrade
            sudo apt-get install python-pip
            sudo apt-get install python3-pip
     3)	Install Numpy:
            pip3 install numpy
            sudo apt-get install libatlas-base-dev
            export PATH=/home/pi/.local/bin:$PATH
            source .bashrc
            sudo reboot
     4)	Install Scipy:
            pip3 install scipy
     5)	Install Deltasigma:
            pip3 install deltasigma
            sudo apt-get install libopenjp2-7
            sudo apt install libtiff5
     6)	Install Tensorflow:
            sudo apt-get install -y libhdf5-dev libc-ares-dev libeigen3-dev
            python3 -m pip install keras_applications==1.0.8 --no-deps
            python3 -m pip install keras_preprocessing==1.1.0 --no-deps
            python3 -m pip install h5py==2.9.0
            sudo apt-get install -y openmpi-bin libopenmpi-dev
            sudo apt-get install -y libatlas-base-dev
            python3 -m pip install -U six wheel mock
            Get latest version for tensorflow: https://github.com/lhelontra/tensorflow-on-arm/releases
            wget https://github.com/lhelontra/tensorflow-on-arm/releases/download/v2.0.0/tensorflow-2.0.0-cp37-none-linux_armv7l.whl
            python3 -m pip install tensorflow-2.0.0-cp37-none-linux_armv7l.whl
     7)	Install Keras:
            pip3 install keras
     8)	Install Webrtcvad:
            pip3 install webrtcvad
     9)	Install Librosa:
            install librosa==0.4.2
     10)	Install Voicecard:  https://wiki.seeedstudio.com/ReSpeaker_4_Mic_Array_for_Raspberry_Pi/
     11)	Install Pyaudio: https://stackoverflow.com/questions/36681836/pyaudio-could-not-import-portaudio

## 3)	Hardware:
   ### a.	Components
The main components of Shazam are shown in figure 1, RPI3B with Raspberry Pi OS Lite system, using the lite system instead of the desktop version to decrease CPU consumption, a StromPi3 is used as a power management board that allows scheduled shut down and start up of the system, a 4-Mic array that records bird voices, a LoRa HAT to transmit the data to a LoRa server (The Things Network) and a INA219 breakout board to monitor the current generated by solar panels. 

![image](https://user-images.githubusercontent.com/64909238/121410144-9218aa00-c962-11eb-9e66-9206d6f2d80f.png)

   ### b.	Setup
The StromPi HAT can be directly connected on the RPI, but the ReSpeaker and the LoRa HAT must be manually connected as shown in figure 2, just follow the color code for each RPi pin and use a breadboard for the common pins between the ReSpeaker and the LoRa HAT (Pin 12).

![image](https://user-images.githubusercontent.com/64909238/121410285-b83e4a00-c962-11eb-8c56-7222bfadd183.png)
  
   ### c.	Specs
   
LoRa HAT:

	- 168 dB maximum link budget
	- +20 dBm - 100 mW constant RF output vs. +14 dBm high efficiency PA
	- Programmable bit rate up to 300 kbps
	- High sensitivity: down to -148 dBm.
	- Bullet-proof front end: IIP3 = -12.5 dBm
	- Low RX current of 10.3 mA, 200 nA register retention
	- Fully integrated synthesizer with a resolution of 61 Hz
	- FSK, GFSK, MSK, GMSK, LoRaTM and OOK modulation.
	- Built-in bit synchronizer for clock recovery
	- Preamble detection.
	- 127 dB Dynamic Range RSSI.
	- Automatic RF Sense and CAD with ultra-fast AFC.
	- Packet engine up to 256 bytes with CRC.
	- Built-in temperature sensor and low battery indicator
	
ReSpeaker 4-Mic Array:

	- 4 analog microphones
	- LED: 12 APA102 programable RGB LEDs, connected to SPI interface
	- Raspberry Pi 40-Pin Headers: compatible with Raspberry Pi Zero and Zero W, Raspberry PiB+, Raspberry Pi 2B, Raspberry Pi 3B, Raspberry Pi 3B+, Raspberry Pi3 A+ and Raspberry Pi 4
	- AC108: highly integrated quad-channel ADC with I2S/TDM output transition
	- I2C: Grove I2C port, connected to I2C-1
	- GPIO12: Grove digital port, connected to GPIO12 & GPIO13
	
INA219:

	- Supply voltage: 6 V (Max)
	- Analog inputs: -26 - 26 V (Differential), -0.3 - 26 V (Common-mode)
	- SDA: GND-0.3 - 6 V
	- SCL: GND-0.3 - Vs+0.3 V
	- Input current into any pin: 5 mA (Max)
	- Operating Temperature: -40 - 125 °C
	- Junction temperature: 150 °C (Max)
	- Storage temperature: -65 - 150 °C


## 4)	Power Consumption
A power monitoring system was developed using INA219 breakout board and RPI. This system is also used to monitor the solar energy input from the solar panels which will be discussed in the Solar Energy section.

![image](https://user-images.githubusercontent.com/64909238/121410698-25ea7600-c963-11eb-815c-4b914d28c62c.png)

Power consumption of the system was tested under different conditions:
    		  
         Default IDLE consumption:	
            - Average Current (mA): 222.40
            - Average Voltage (V): 5.20
            - Average Power (W): 1.16
           
         Power consumption during running the Shazam while turning off USB, LAN, HDMI, LEDs and BT:
            - Average Current (mA): 272.29
            - Average Voltage (V): 5.19
            - Average Power (W): 1.41
              
Effect of turning off different peripherals of RPi:


This test was done on RPI 3B+. First, default current consumption was measured, and it was 456.4 mA, then each peripheral was turned off separately and the current consumption for each peripheral turned off and the numbers shown are the new consumption after turning off each peripheral subtracted from the default consumption. 

![image](https://user-images.githubusercontent.com/64909238/121412278-cee5a080-c964-11eb-9e72-4838d6181276.png)


## 5)	Solar Energy to Power Shazam
The solar energy system shown in figure 5 was designed to power the RPi.

![image](https://user-images.githubusercontent.com/64909238/121412514-166c2c80-c965-11eb-957f-dd91ee76c0c7.png)

	Average Current Consumption: 300 mA
	Solar Panels: 2 x 17 V / 10 W
	Surface Area = 0.116 m² 
	Efficiency = 17 %
	Average daily power output for 12 sunny hours: 20(W) * 0.17 * 12(h) = 40.8 Wh
	Average daily current output = 2400 mAh
	Li-ion Battery Capacity = 4800 mAh


## 6)	LoRa transmissions
An open source lmic based code is used to transmit data to a LoRa gateway, the code can be found in this link: https://github.com/wklenk/lmic-rpi-lora-gps-hat , WiringPi library have to be installed first, then the LoRa file can run. 
Our LoRa transmission algorithm basically reads the json data file that is created by the main bird sound detection algorithm, for each data entry, the highest 3 probabilities are read, in addition to the timestamp data and the current readings from the INA219, then if the highest bird id probability is higher than 0.2, the data is transmitted over LoRa using the LoRaWAN HAT to TTN, otherwise the data entry is skipped and the algorithm checks the next one. The whole process is showed in figure 8 and the python file responsible for it is lora.py file.

![image](https://user-images.githubusercontent.com/64909238/121415580-30f3d500-c968-11eb-8ace-9ec6826b1ec5.png)


## 7)	Power management
Since Raspberry Pi does not have a built-in power management system, an external power management system is used to schedule the working hours of the detection system to reduce the overall power consumption during the times when there is no bird activity expected. 
We use the StromPi 3 power management board since it has the specs and capabilities we need for our system, the WakeUp-Alarm mode starts the RPi at a predefined time, while the PowerOff-Alarm mode shuts down the RPi at a predefined time.
Preparing the scheduled shutdown and power up:
	
	a. Set the real time clock (RTC) by synchronizing it with the RPi time.
	b. Set the PowerOff-Alarm mode to shutdown the RPi everyday at a certain time.
	c. Set WakeUp-Alarm mode at alarm mode 1 to start the RPi everyday at a certain time.
	d. Activate Power save mode to reduce StromPi power consumption.
	e. Activate serialless mode to allow other HATs to use serial connection with RPi.
	
	
## 8)	Running shazam
To run shazam after the complete installation of the system, simply run the "shazam.py" file and it will take care of the whole process as shown in the process flowchart.

Shazam.py works as follows:

		1. Runs the main.py file responsible for bird voice detection
		2. main.py file detects any surrounding voices and writes a report of each detection in a json file (/bird_data/data_n.json)
		3. After 30 minutes it runs lora.py file which access the json files, checks each detection if there is a high probability (higher than 0.2) of a certain bird then transmit the data over LoRa using the LoRa HAT

Files locations:

	"main.py": "/Shazam4Nature-master-3/pi_main/"
	"lora.py": "/Shazam4Nature-master-3/pi_main/lmic-rpi-lora-gps-hat/examples/periodic"

![image](https://user-images.githubusercontent.com/64909238/121417337-13c00600-c96a-11eb-84f3-357d15ffc4b7.png)

## 9)	Imortant files and directories

	- Shazam4Nature-master-3/pi_main/main.py : Main python file that includes the bird sound detection algorithm using ReSpeaker 4-mic array.
	- Shazam4Nature-master-3/pi_main/mic_array.py : ReSpeaker 4-mic array based code for recording sound
	- Shazam4Nature-master-3/pi_main/recognition/recognition.py : Loads the CNN model and predicts the bird type
	- Shazam4Nature-master-3/pi_main/bird_data/ : Directory that keeps the bird sound recognition reports as json files
	- Shazam4Nature-master-3/pi_main/lmic-rpi-lora-gps-hat/examples/periodic/main.c : Main C file that controls the LoRa tranmission process, payload, keys and LoRa configuration must be editted in this file. We control the file using lora.py file, so no need to edit anything inside. The main.c file is compiled and creates an executable called periodic.out that must run to transmit the payload.
	- Shazam4Nature-master-3/pi_main/lmic-rpi-lora-gps-hat/examples/periodic/build/periodic.out : Executable that runs the LoRa process
	. Shazam4Nature-master-3/pi_main/lmic-rpi-lora-gps-hat/examples/periodic/lora.py : Python file that controls the LoRa tranmission process (main.c and periodic.out). It This file reads data from json files that include sound recognition reports and edit main.c accordingly before running periodic.out.
	

## References

	https://wiki.seeedstudio.com/ReSpeaker_4_Mic_Array_for_Raspberry_Pi/
	https://learn.adafruit.com/adafruit-ina219-current-sensor-breakout/python-circuitpython
	https://pinout.xyz/
	https://pinout.xyz/pinout/respeaker_4_mic_array
	https://www.pidramble.com/wiki/benchmarks/power-consumption
	https://strompi.joy-it.net/files/files/downloads/anleitungen/RB-StromPi3-Manual-13-10-20.pdf
	https://learn.adafruit.com/adafruit-ina219-current-sensor-breakout/wiring
	https://www.raspberrypi.org/documentation/hardware/raspberrypi/power/README.md
	https://www.hackster.io/chrisb2/raspberry-pi-ina219-voltage-current-sensor-library-f3bb54
	https://cdn.shopify.com/s/files/1/0176/3274/files/Raspberry-Pi-Comparison_r4.pdf?3484
	https://github.com/wklenk/lmic-rpi-lora-gps-hat
	https://www.thethingsnetwork.org/article/selecting-the-best-lithium-primary-batteries-for-your-lorawan-node
	https://wiki.dragino.com/index.php?title=Lora/GPS_HAT
	https://www.dragino.com/downloads/downloads/LoRa-GPS-HAT/LoRa_GPS_HAT_UserManual_v1.0.pdf
	https://howchoo.com/g/mmfkn2rhoth/raspberry-pi-solar-power
	https://www.ti.com/lit/ds/symlink/ina219.pdf
	https://www.adafruit.com/product/1944
