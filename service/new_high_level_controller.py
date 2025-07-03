import pandas as pd

import time
import os

from service.arduino_comm import get_encoder_value, set_encoder_value

E = 35000
BASE_DIR = ""
curl_flextion = None
curl_extension = None

_data_initialized = False

e_0 = 0
theta_0 = 0
e_curr = 0
theta_curr = 0
no_of_reps = 1

def set_e_0(e_val):
    global e_0
    e_0 = e_val

def set_theta_0(theta_val):
    global theta_0
    theta_0 = theta_val

def set_number_of_reps(reps):
    global no_of_reps
    no_of_reps=reps

def init_data():
    global _data_initialized
    if not _data_initialized:
        global BASE_DIR
        global curl_flextion
        global curl_extension

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        curl_flextion = pd.read_csv(os.path.join(BASE_DIR, 'data', 'curl_flexion.csv'))
        curl_extension = pd.read_csv(os.path.join(BASE_DIR, 'data', 'curl_extension.csv'))

        _data_initialized = True

def ensure_data(func):
    def wrapper(*args, **kwargs):
        init_data()
        return func(*args, **kwargs)
    return wrapper

def init_e_0():
    global e_0
    get_encoder_value(set_e_0)

def init_theta_0():
    global theta_0
    set_theta_0(155)

@ensure_data
def get_closest_lower_theta(input_theta):
    theta_values = curl_flextion.iloc[:, 1]
    lower_thetas = theta_values[theta_values < input_theta]

    if lower_thetas.empty:
        return None

    return lower_thetas.max()

def get_curr_e_val(theta_curr):
    return (E / 360) * (theta_curr - theta_0) + e_0


@ensure_data
def perform_reps():
    global theta_0
    global no_of_reps
    
    print(no_of_reps, theta_0)

    start_theta_value = get_closest_lower_theta(theta_0)

    start_index = curl_flextion[curl_flextion.iloc[:, 1] == start_theta_value].index
    if start_index.empty:
        print("Start theta not found in flexion data.")
        return

    start_index = start_index[0]

    for rep in range(no_of_reps):
        print(f"\nRepetition {rep + 1}/{no_of_reps} – Flexion")

        # Flexion phase
        for i in range(start_index, len(curl_flextion)):
            start_time = time.time()
            theta_val = curl_flextion.iloc[i, 1]
            curr_e_val = get_curr_e_val(theta_val)
            print(f"Flexion: Theta = {theta_val}, Encoder = {curr_e_val}")
            set_encoder_value(int(curr_e_val))
            elapsed = time.time() - start_time
            print("Elapsed Time: ",elapsed)
            remaining = max(0.0, 0.05 - elapsed)
            time.sleep(remaining)

        time.sleep(2)

        print(f"\nRepetition {rep + 1}/{no_of_reps} – Extension")

        # Extension phase
        for i in range(len(curl_extension)):
            start_time = time.time()
            theta_val = curl_extension.iloc[i, 1]
            curr_e_val = get_curr_e_val(theta_val)
            print(f"Extension: Theta = {theta_val}, Encoder = {curr_e_val}")
            set_encoder_value(curr_e_val)
            elapsed = time.time() - start_time
            print("Elapsed Time: ",elapsed)
            remaining = max(0.0, 0.05 - elapsed)
            time.sleep(remaining)

        time.sleep(2)
