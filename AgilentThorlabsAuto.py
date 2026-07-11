#By HARRISH KARUNAKARAN @ Fradin Group

import time
import csv
import Keysight_E3631A as keysight
import matplotlib.pyplot as graph
import PM16
import statistics
from datetime import datetime
import serial
import math

#------------
#Change these!
#------------

#Check Port Name through Terminal then change here!
power_supply = keysight.Keysight_E3631A(port='port_name', baudrate=9600, parity=None, data=8, timeout=1, _sound=True)
#Check VISA through visachecker.py and then change here!
pm = PM16.PM16('port_name')
#Check Arduino through __ and then change here!
board = serial.Serial('port_name', 9600, timeout=1)

'''
Measuring Current + Power? -> exp_type = 1
Measuring Time + Power? -> exp_type = 2
Measure Time, Current & Power? -> exp_type = 3
'''
exp_type = None

#Set your current increase interval here.
current_increase_interval = 0.1

#Is it a conditional current increase?
custom_current = False

#How many times are we doing this?
iterations = 1

#-----------
#Keep as is.
#-----------

current = 0.0
max_current = 4.01
time_interval = 5.0
power_supply.P6V_voltage = 6.0
dormant_time = 5
points = 10
time_between_measurements = 0.5
wavelength = 633
perp_coil_on = board.readline().decode().strip
para_coil_on = board.readline().decode().strip

measured_currents = []
measured_time = []
measured_power = []
measured_coil_status = []
avg_power = []
stdev_power = []
new_coil_status = []
new_currents = []
new_time = []

coil_map = {(False, False): "OFF", (False, True): "BT", (True,False): "BII", (True, True): "Both"}

pm.set_wavelength(wavelength)

def current_check():
	global current_increase_interval
	if power_supply.P6V_current < 1:
		current_increase_interval = 0.05
	else:
		current_increase_interval = 0.2

def record_raw_data():
	measured_coil_status.apppend(coil_check())
	measured_currents.append(power_supply.P6V_current)
	measured_time.append((time.time() - start_time))
	measured_power.append((pm.power()*24000))
	csvwriter.writerow([measured_time[-1], measured_currents[-1], measured_coil_status[-1], measured_power[-1]])
	csvfile2.flush()

def record_comp_data():
	new_coil_status.append(coil_check())
	stdev_power.append(statistics.stdev(measured_power[-(points-1):]))
	avg_power.append(statistics.mean(measured_power[-(points-1):]))
	new_currents.append(power_supply.P6V_current)
	new_time.append((time.time() - start_time))

def create_graph(exp_type):
	if exp_type == 1:
		graph.errorbar(new_currents, avg_power, yerr=stdev_power, fmt='o')
		graph.xlabel("Current (A)")
		graph.ylabel("Power (mW)")
		graph.grid(True)
		graph.show()
	elif exp_type == 2:
		graph.plot(measured_time, measured_power)
		graph.xlabel("Time (s)")
		graph.ylabel("Power (mW)")
		graph.grid(True)
		graph.show()

def time_run(measurement_time):
	end_time = time.time() + measurement_time
	while time.time() < end_time:
		record_raw_data()
		time.sleep(time_between_measurements)

def current_run(x):
	global current
	while current <= max_current:
		power_supply.P6V_current = current
		time.sleep(time_interval)
		parallel_coil_on(3)
		record_data()
		perpendicular_coil_on(3)
		record_data()
		if custom_current == True:
			current_check()
		current += x

def record_data():
	for q in range(points):
		record_raw_data()
		time.sleep(time_between_measurements)
	record_comp_data()

#Coil controls

def perpendicular_coil_on(time_coil_on):
	global para_coil_on
	global perp_coil_on
	board.write(("PERP_ON" + '\n').encode())
	perp_coil_on = True
	time.sleep(time_coil_on)

def parallel_coil_on(time_coil_on):
	global para_coil_on
	global perp_coil_on
	board.write(("PARA_ON" + '\n').encode())
	para_coil_on = True
	perp_coil_on = False
	time.sleep(time_coil_on)

def both_coils_off(time_coil_on):
	global para_coil_on
	global perp_coil_on
	board.write(("OOF" + '\n').encode())
	para_coil_on = True
	perp_coil_on = False
	time.sleep(time_coil_on)

def coil_check():
	coil_status = coil_map[(para_coil_on, perp_coil_on)]
	return coil_status

def return_data(x):
	if x == 1:
		with open(f"current_data_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv", "w", newline='') as csvfile:
			csvwriter = csv.writer(csvfile)
			csvwriter.writerow(["Coil Status", "Current (A)", "Average Power (mW)", "Standard Deviation"])
			for i in range(len(new_currents)):
				csvwriter.writerow([new_coil_status[i], new_currents[i], avg_power[i], stdev_power[i]])
	elif x == 2:
		with open(f"current_data_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv", "w", newline='') as csvfile:
			csvwriter = csv.writer(csvfile)
			csvwriter.writerow(["Time(s)", "Average Power (mW)"])
			for i in range(len(measured_time)):
				csvwriter.writerow([measured_time[i], avg_power[i]])
	elif x == 3:
		with open(f"current_data_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv", "w", newline='') as csvfile:
			csvwriter = csv.writer(csvfile)
			csvwriter.writerow(["Time(s)", "Coil Status", "Current (A)" "Average Power (mW)", "Standard Deviation"])
			for i in range(len(new_time)):
				csvwriter.writerow([new_time[i], new_coil_status[i], new_currents[i], avg_power[i], stdev_power[i]])
	else:
		raise ValueError("Please select a valid integer for experiment type.")


with open(f"raw_current_data_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv", "w", newline='') as csvfile2:
	csvwriter = csv.writer(csvfile2)
	csvwriter.writerow(["Time (s)", "Current (A)", "Power (mW)"])
	start_time = time.time()
	both_coils_off(0)
	for i in range(iterations):
		current = 0.0
		if exp_type == 1:
			current_run(current_increase_interval)
		elif exp_type == 2:
			time_run(0)

return_data(exp_type)
create_graph(exp_type)
