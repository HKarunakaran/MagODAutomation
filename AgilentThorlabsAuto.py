#By HARRISH KARUNAKARAN @ Fradin Group

import time
import csv

import numpy as np
import matplotlib
matplotlib.use('WebAgg')
import Keysight_E3631A as keysight
import matplotlib.pyplot as graph
import PM16
import statistics
from datetime import datetime
import serial
import math
from scipy import stats
from decimal import Decimal, getcontext
import mpmath

#------------
#Change these!
#------------

#Check Port Name through Terminal then change here!
power_supply = keysight.Keysight_E3631A(port='COM1', baudrate=9600, parity=None, data=8, timeout=1, _sound=True)
#Check VISA through visachecker.py and then change here!
pm = PM16.PM16('USB0::0x1313::0x807B::15092508::0::INSTR')
pm2 = PM16.PM16('USB0::0x1313::0x807B::17032439::0::INSTR')
#Check Arduino through __ and then change here!
board = serial.Serial('COM3', 9600, timeout=1)

'''
OD + CMag + Power -> exp_type = 1
Measuring Time + Power? -> exp_type = 2
Measure Time, Current & Power? -> exp_type = 3
'''
exp_type = 1

#Set your current increase interval here.
current_increase_interval = 0.5

#Is it a conditional current increase?
custom_current = False

#How many times are we doing this?
sample_numbers = 1

#How long are you measuring for?
measurement_time = 3600

#-----------
#Keep as is.
#-----------


current = 0.0
max_current = 4.01
time_interval = 5.0
power_supply.P6V_voltage = 6.0
dormant_time = 5
points = 10
time_between_measurements = 0.3
wavelength = 633
pm_factor = 1000
pm2_factor = 1000
perp_coil_on = board.readline().decode().strip
para_coil_on = board.readline().decode().strip
pm.set_wavelength(wavelength)
pm2.set_wavelength(wavelength)
if exp_type == 1: blank_req = True 
else: blank_req = False

measured_currents = []
measured_time = []
measured_power = []
measured_power2 = []
adjusted_sample_power = []
measured_coil_status = []
avg_power = []
avg_power2 = []
stdev_power = []
stdev_power2 = []
new_coil_status = []
new_currents = []
new_time = []
cal1_array = []
cal2_array = []
cal3_array = []
od = []
cmag = []

while blank_req:
    confirmation_step1 = input("Please ensure nothing is in the holder. Type YES to proceed.")
    if confirmation_step1 == "YES":
        print("Thank you! Measuring correction factor now...")
        break



for i in range(100):
    cal1_array.append(pm.power()*pm_factor)
    cal2_array.append(pm2.power()*pm2_factor)
    cal3_array.append(cal1_array[-1]/cal2_array[-1])
    time.sleep(0.2)
    #print(str(cal1_array[-1]) + ' ' + str(cal2_array[-1]) + ' ' + str(cal3_array[-1]))
correction_factor = statistics.fmean(cal3_array)
print("Correction factor: " + str(correction_factor))

while blank_req:
    confirmation_step2 = input("Please add your blank. Type YES to proceed.")
    if confirmation_step2 == "YES":
        print("Thank you! Measurements underway...")
        break

measured_power2.append(pm2.power()*pm2_factor)
measured_power.append(pm.power()*pm_factor)
measured_time.append(0)

coil_map = {(False, False): "OFF", (False, True): "BT", (True,False): "BII", (True, True): "Both"}

def current_check():
    global current_increase_interval
    if power_supply.P6V_current < 1:
        current_increase_interval = 0.05
    else:
        current_increase_interval = 0.2

def record_raw_data():
    measured_coil_status.append(coil_check())
    measured_power2.append(pm2.power() * pm2_factor)
    measured_power.append((pm.power() * pm_factor))
    measured_currents.append(power_supply.P6V_current)
    measured_time.append((time.perf_counter_ns() - start_time)/1e9)
    csvwriter.writerow([measured_time[-1], measured_currents[-1], measured_coil_status[-1], measured_power[-1], measured_power2[-1]])
    csvfile2.flush()

def record_comp_data():
    new_coil_status.append(coil_check())
    stdev_power.append(statistics.stdev(measured_power[-(points-1):]))
    stdev_power2.append(statistics.stdev(measured_power2[-(points-1):]))
    avg_power.append(statistics.fmean(measured_power[-(points-1):]))
    avg_power2.append(statistics.fmean(measured_power2[-(points-1):]))
    new_currents.append(power_supply.P6V_current)
    new_time.append((time.perf_counter_ns() - start_time)/1e9)

def record_od():
    getcontext().prec = 30
    csvwriter.writerow(" ")
    csvwriter.writerow(["OD"])
    for i in range(len(avg_power)):
        print(str(len(avg_power)) + " " + str(avg_power) + " " + str(avg_power2))
        od.append(Decimal(str((avg_power2[i]*correction_factor)/avg_power[i])).log10())
        csvwriter.writerow([od[-1]])
        csvfile2.flush()

def determine_cmag():
    for o, i in enumerate(new_coil_status):
        if i == "BII":
            cmag.append(Decimal(str(od[o]))/Decimal(str(od[o + 1])))
        else:
            cmag.append(float('nan'))
            
def create_graph(exp_type):
    if exp_type == 1:
        whole, grphs = graph.subplots(3)
        grphs[0].plot(new_currents, [float(x) for x in od], marker = "o")
        grphs[0].set_title("OD vs Current")
        grphs[1].plot(new_currents, [float(x) for x in cmag], marker = "o")
        grphs[1].set_title("CMag vs Current")
        grphs[2].errorbar(new_currents, avg_power, yerr = stdev_power, capsize = 3, marker = "o")
        grphs[2].errorbar(new_currents, avg_power2, yerr = stdev_power2, capsize = 3, marker = "o")
        grphs[2].set_title("Power Meters vs Current")
        for ax in grphs:
            ax.grid(True)
        whole.tight_layout()
        graph.show()
       
    elif exp_type == 2:
        graph.plot(measured_time, measured_power,color='blue', label="PM1")
        graph.plot(measured_time, measured_power2, color='red', label="PM2")
        graph.legend()
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
        both_coils_off(3)
        record_data()
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
    para_coil_on = False
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
    para_coil_on = False
    perp_coil_on = False
    time.sleep(time_coil_on)

def coil_check():
    coil_status = coil_map[(para_coil_on, perp_coil_on)]
    return coil_status

def return_data(x):
    if x == 1:
        with open(f"current_data_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv", "w", newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(["Coil Status", "Current (A)", "OD", "CMag" "Average Power 1 (mW)", "Standard Deviation 1", "Average Power 2 (mW)", "Standard Deviation 2"])
            for i in range(len(new_currents)):
                csvwriter.writerow([new_coil_status[i], od[i], cmag[i], new_currents[i], avg_power[i], stdev_power[i], avg_power2[i], stdev_power2[i]])
    elif x == 2:
        with open(f"current_data_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv", "w", newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(["Time(s)", " Power1 (mW)", " Power2 (mW)"])
            for i in range(len(measured_time)):
                csvwriter.writerow([measured_time[i], measured_power[i], measured_power2[i]])
    else:
        raise ValueError("Please select a valid integer for experiment type.")


with open(f"raw_current_data_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv", "w", newline='') as csvfile2:
    csvwriter = csv.writer(csvfile2)
    csvwriter.writerow(["Time (s)", "Current (A)", "Power (mW)"])
    start_time = time.time()
    both_coils_off(0)
    for i in range(sample_numbers):
        current = 0.0
        if exp_type == 1:
            current_run(current_increase_interval)
        elif exp_type == 2:
            time_run(measurement_time)
        else:
            continue
    record_od()
    determine_cmag()

return_data(exp_type)
create_graph(exp_type)


board.close()



"""
   mean = []
   stdev = []
   median = []
   teatime = []
   mean_err = []
   stdev_err = []
   median_err = []
   teatime_err = []

   with open(f"con_test_hahaha_getit_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv", "w", newline='') as csvfile3:
       csvwriter = csv.writer(csvfile3)
       csvwriter.writerow(["Measurement Duration (s)", "Mean (mW)", "Standard Deviation", "Median(mW)"])
    teatime.append(str(p*0.2))
    fmeanie = statistics.fmean(cal3_array)
    stdevie = statistics.stdev(cal3_array)
    medie = statistics.median(cal3_array)
    mean.append(str(fmeanie))
    stdev.append(str(stdevie))
    median.append(str(medie))
    mean_err.append((fmeanie/np.sqrt(p)))
    stdev_err.append((stdevie/np.sqrt(2*p)))
    median_err.append((1.253*(fmeanie/np.sqrt(p))))
    csvwriter.writerow([teatime[-1], mean[-1], stdev[-1], median[-1]])
    csvfile3.flush()
        print("Duration (s) " + str(teatime[-1]))
        print("Mean " + str(mean[-1]))
        print("Stdev " + str(stdev[-1]))
        print("Median " + str(median[-1]))
   whole, grphs = graph.subplots(3)
    grphs[0].errorbar([float(x) for x in teatime], [float(x) for x in mean], yerr = mean_err,capsize = 3, marker = "o")
    grphs[0].set_title("Mean vs Time")
    grphs[1].errorbar([float(x) for x in teatime], [float(x) for x in stdev], yerr = stdev_err, capsize = 3, marker = "o")
    grphs[1].set_title("Stdev vs Time")
    grphs[2].errorbar([float(x) for x in teatime], [float(x) for x in median], yerr = median_err, capsize =3, marker = "o")
    grphs[2].set_title("Median vs Time")
    for ax in grphs:
        ax.grid(True)
    whole.tight_layout()
    graph.show()
    """