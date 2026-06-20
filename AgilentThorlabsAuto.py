#By HARRISH KARUNAKARAN

import time
import csv
import Keysight_E3631A as keysight
import matplotlib.pyplot as graph
import PM16
import statistics
from datetime import datetime


#Check Port Name through Terminal then change here!
power_supply = keysight.Keysight_E3631A(port='port_name', baudrate=9600, parity=None, data=8, timeout=1, _sound=True)
#Check VISA through visachecker.py and then change here!
pm = PM16('port_name')

current = 0.0
current_increase_interval = 0.2
max_current = 4.0
time_interval = 5.0
iterations = 10
power_supply.P6V_voltage = 6.0
dormant_time = 5
points = 10
time_between_measurements = 0.1
wavelength = 633

measured_currents = []
measured_time = []
measured_power = []
avg_power = []
stdev_power = []

pm.set_wavelength(wavelength)

#I need more measurements and more error over a timeframe

def record_data():
	measured_currents.append(power_supply.P6V_current)
	measured_time.append((time.time() - start_time))
	measured_power.append((pm.power()*24000))
	csvwriter.writerow([measured_time[-1], measured_currents[-1],measured_power[-1]])
	csvfile.flush()

def calculate_data():
	stdev_power.append(statistics.stdev(measured_power[-(points-1):]))
	avg_power.append(statistics.mean(measured_power[-(points-1):]))

with open(f"raw_current_data_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv", "w", newline='') as csvfile2:
	csvwriter = csv.writer(csvfile2)
	csvwriter.writerow(["Time (s)", "Current (A)", "Power (mW)"])
	start_time = time.time()
	for i in range(iterations):
		current = 0.0
		#time.sleep(dormant_time)
		while current <= max_current:
			power_supply.P6V_current = current
			time.sleep(time_interval)
			for q in range(points):
				record_data()
				time.sleep(time_between_measurements)
			calculate_data()
			current += current_increase_interval

with open(f"current_data_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv", "w", newline='') as csvfile:
	csvwriter = csv.writer(csvfile)
	csvwriter.writerow(["Current (A)", "Average Power (mW)", "Standard Deviation"])
	for i in measured_currents:
		csvwriter.writerow([measured_currents[i], avg_power[i], stdev_power[i]])

graph.errorbar(measured_currents, avg_power, yerr=stdev_power, fmt='o')
graph.xlabel("Current (A)")
graph.ylabel("Power (mW)")
graph.grid(True)
graph.show()

