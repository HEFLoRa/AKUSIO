#!/usr/bin/python3
import os
os.chdir('/home/pi/Shazam4Nature-master-3/pi_main/lmic-rpi-lora-gps-hat/examples/periodic/')

import subprocess
import time
import json
import numpy as np
import sys
import re

global timestamp
global time
global date
global prob
global prob_1
global prob_2
global prob_3
global id_1
global id_2
global id_3
global prob
global current
global voltage

prob = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 
	6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 
	13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18:0 
	}

#FILE_NAME = "/home/pi/Shazam4Nature-master-3/pi_main/bird_data/data_0.json"

# Converts timestamp data from json files to an array.
def timestamp_converter(timestamp):
	timestamp_conv = ""
	hour = ""
	min = ""
	sec = ""
	day = ""
	month = ""
	year = ""
	for element in range(0,len(timestamp)):
		if re.search(r'[0-9]',timestamp[element]):
			timestamp_conv = timestamp_conv + timestamp[element]
		elif re.search(r'[.]',timestamp[element]):
			break
	for y in range(2,3):
		if int(timestamp_conv[y]) != 0:
			year = year + timestamp_conv[y]
	for y in range(3,4):
                year = year + timestamp_conv[y]
	for m in range(4,5):
		if int(timestamp_conv[m]) != 0:
			month = month + timestamp_conv[m]
	for m in range(5,6):
                month = month + timestamp_conv[m]
	for d in range(6,7):
		if int(timestamp_conv[d]) != 0:
			day = day + timestamp_conv[d]
	for d in range(7,8):
                day = day + timestamp_conv[d]
	for h in range(8,9):
		if int(timestamp_conv[h]) != 0:
			hour = hour + timestamp_conv[h]
	for h in range(9,10):
                hour = hour + timestamp_conv[h]
	for m in range(10,11):
		if int(timestamp_conv[m]) != 0:
			min = min + timestamp_conv[m]
	for m in range(11,12):
                min = min + timestamp_conv[m]
	for s in range(12,13):
		if int(timestamp_conv[s]) != 0:
			sec = sec + timestamp_conv[s]
	for s in range(13,14):
                sec = sec + timestamp_conv[s]
	timestamp_arr = np.array([year, month, day, hour, min, sec])
	return timestamp_arr

# Read data from json files that contains sound recognition reports.
def read_json(i, file_name):
	global prob
	global time_stamp
	global current
	global voltage
	with open(file_name) as file:
		data = file.read()
		obj = json.loads(data)
		time_stamp_raw = obj[i]['timestamp']
		time_stamp = timestamp_converter(str(time_stamp_raw))
		current = obj[i]['solar_current']
		voltage = obj[i]['solar_voltage']
		for id in range(len(prob)):
			prob[id] = obj[i]['classifications'][id]['probability']

# Determine the top 3 bird type probabilities.
def determine_max():
	global prob_array
	global id_array
	prob_1 = prob_2 = prob_3 = -sys.maxsize
	id_1 = id_2 = id_3 = -sys.maxsize
	for i in range(0, len(prob)):
		if prob[i] > prob_1:
			prob_3 = prob_2
			id_3 = id_2
			prob_2 = prob_1
			id_2 = id_1
			prob_1 = prob[i]
			id_1 = i
		elif prob[i] > prob_2:
			prob_3 = prob_2
			id_3 = id_2
			prob_2 = prob[i]
			id_2 = i
		elif prob[i] > prob_3:
			prob_3 = prob[i]
			id_3 = i
	prob_array = np.array([prob_1, prob_2, prob_3])
	id_array = np.array([id_1, id_2, id_3])
	print(prob_array)
	print(id_array)
	
# Delete old variables from main.c files.
def delete():
	filename = 'main.c'
	initial_line = 1
	file_lines = {}

	with open(filename) as f:
		content = f.readlines() 
	for line in content:
		file_lines[initial_line] = line.strip()
		initial_line += 1
	f = open(filename, "w")
	for line_number, line_content in file_lines.items():
		if line_number > 14:
			f.write('{}\n'.format(line_content))
	f.close()

# Write new data as variable in the main.c files
def write_data():
	global id
	global per
	global prob_array
	global id_array
	global time_stamp
	global current
	global voltage
	with open("main.c",'r+') as contents:
      		save = contents.read()
	with open("main.c",'w') as contents:
		contents.write("int id_1 = " + str(id_array[0]) + ";\n")
		contents.write("int id_2 = " + str(id_array[1]) + ";\n")
		contents.write("int id_3 = " + str(id_array[2]) + ";\n")
		contents.write("float prob_1 = " + str(prob_array[0]) + ";\n")
		contents.write("float prob_2 = " + str(prob_array[1]) + ";\n")
		contents.write("float prob_3 = " + str(prob_array[2]) + ";\n")
		contents.write("int year = " + str(time_stamp[0]) + ";\n")
		contents.write("int month = " + str(time_stamp[1]) + ";\n")
		contents.write("int day = " + str(time_stamp[2]) + ";\n")
		contents.write("int hour = " + str(time_stamp[3]) + ";\n")
		contents.write("int min = " + str(time_stamp[4]) + ";\n")
		contents.write("int sec = " + str(time_stamp[5]) + ";\n")
		contents.write("float current = " + str(current) + ";\n")
		contents.write("float voltage = " + str(voltage) + ";\n")
	with open("main.c",'a') as contents:
		contents.write(save)

# Compiles the main.c files, runs periodic.out executable and kills both processes after one minute.
def run_process():
	subprocess.run("make")
	subprocess.Popen(["sudo", "./build/periodic.out"])
	time.sleep(60)
	subprocess.Popen(["sudo", "killall", "./build/periodic.out"])
	print("Exit!")

def main():
	global prob_array
	path = "/home/pi/Shazam4Nature-master-3/pi_main/bird_data/"
	for filename in os.listdir(path):
		print("Opening " + filename + " ....")
		with open(path + filename) as file:
			data = file.read()
			obj = json.loads(data)
			print("Number of iterations:")
			print(len(obj))
			r = len(obj) 
		for it in range(r):
			print("Tranmission number:" + str(it))
#			it = 1
			read_json(it, path+filename)
			determine_max()
			if prob_array[0] >= 0.2:
				delete()
				write_data()
				run_process()
				time.sleep(10)
			else:
				print("Skipping")
		time.sleep(600)
		

if __name__ == '__main__':
    main()

