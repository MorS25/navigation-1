# load a px4_sdlog2 csv file

import csv
import math
import numpy as np
import re

from nav.structs import IMUdata, GPSdata, Airdata, NAVdata

d2r = math.pi / 180.0

def load(csv_base):
    result = {}

    comb_path = csv_base + '_sensor_combined_0.csv'
    gps_path = csv_base + '_vehicle_gps_position_0.csv'
    filt_path = csv_base + '_vehicle_global_position_0.csv'

    result['imu'] = []
    with open(comb_path, 'rb') as f:
        reader = csv.DictReader(f)
        for row in reader:
            imu = IMUdata()
            imu.time = float(row['timestamp']) / 1000000.0
            imu.p = float(row['gyro_rad[0]'])
            imu.q = float(row['gyro_rad[1]'])
            imu.r = float(row['gyro_rad[2]'])
            imu.ax = float(row['accelerometer_m_s2[0]'])
            imu.ay = float(row['accelerometer_m_s2[1]'])
            imu.az = float(row['accelerometer_m_s2[2]'])
            hx = float(row['magnetometer_ga[0]'])
            hy = float(row['magnetometer_ga[0]'])
            hz = float(row['magnetometer_ga[0]'])
            hf = np.array( [hx, hy, hz] )
            norm = np.linalg.norm(hf)
            hf /= norm
            imu.hx = hf[0]
            imu.hy = hf[1]
            imu.hz = hf[2]
            #print imu.hx, imu.hy, imu.hz
            imu.temp = 15.0
            result['imu'].append( imu )

    result['gps'] = []
    with open(gps_path, 'rb') as f:
        reader = csv.DictReader(f)
        for row in reader:
            gps = GPSdata()
            gps.time = float(row['timestamp']) / 1000000.0
            gps.unix_sec = float(row['time_utc_usec']) / 1000000.0
            gps.lat = float(row['lat'])
            gps.lon = float(row['lon'])
            gps.alt = float(row['alt'])
            gps.vn = float(row['vel_n_m_s'])
            gps.ve = float(row['vel_e_m_s'])
            gps.vd = float(row['vel_d_m_s'])
            gps.sats = int(row['satellites_used'])
            if gps.sats >= 5:
                result['gps'].append(gps)

    result['air'] = []
    with open(gps_path, 'rb') as f:
        reader = csv.DictReader(f)
        for row in reader:
            air = Airdata()
            air.time = imu.time
            air.static_press = float(row['SENS_BaroPres'])
            air.diff_press = float(row['SENS_DiffPres'])
            air.temp = float(row['AIRS_AirTemp'])
            air.airspeed = float(row['AIRS_IndSpeed'])
            air.alt_press = float(row['SENS_BaroAlt'])
            air.alt_true = gps.alt
            result['air'].append( air )
        
    result['filter'] = []
    with open(filt_path, 'rb') as f:
        reader = csv.DictReader(f)
        for row in reader:
            nav = NAVdata()
            nav.time = float(row['timestamp']) / 1000000.0
            nav.lat = float(row['lat'])*d2r
            nav.lon = float(row['lon'])*d2r
            nav.alt = float(row['alt'])
            nav.vn = float(row['vel_n'])
            nav.ve = float(row['vel_e'])
            nav.vd = float(row['vel_d'])
            nav.phi = float(row['  ATT_Roll'])
            nav.the = float(row['ATT_Pitch'])
            psi = float(row['ATT_Yaw'])
            if psi > 180.0:
                psi = psi - 360.0
            if psi < -180.0:
                psi = psi + 360.0
            nav.psi = psi
            result['filter'].append(nav)

    #result['pilot'] = []
    #result['act'] = []
    #result['ap'] = []

    return result
