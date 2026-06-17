#By HARRISH KARUNAKARAN

import time
import csv
import Keysight_E3631A as keysight
import matplotlib.pyplot as plt
from datetime import datetime


#Check Port Name through Terminal then Change here!
power_supply = keysight.Keysight_E3631A(port='port_name', baudrate=9600, parity=None, data=8, timeout=1, _sound=True)

current = 0.0
current_increase_interval = 0.2
max_current = 4.0
time_interval = 1.0
iterations = 10
power_supply.P6V_voltage = 6.0
dormant_time = 5

measured_currents = []
measured_time = []

with open(f"current_data_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv", "w", newline='') as csvfile:
	csvwriter = csv.writer(csvfile)
	csvwriter.writerow(["time", "current"])
	for i in range(iterations):
		current = 0.0
		time.sleep(dormant_time)
		while current < max_current:
			power_supply.P6V_current = current
			time.sleep(time_interval)
			measured_currents.append(power_supply.P6V_current)
			measured_time.append(datetime.now().isoformat())
			csvwriter.writerow([measured_time[-1], measured_currents[-1]])
			csvfile.flush()
			current += current_increase_interval

plt.plot(measured_time,measured_currents)
plt.grid(True)
plt.show()

