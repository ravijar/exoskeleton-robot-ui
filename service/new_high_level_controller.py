import pandas as pd

import time

from service.arduino_comm import get_encoder_value

E = 35000

e_0 = 0
theta_0 = 0
e_curr = 0
theta_curr = 0
no_of_reps = 0

curl_flextion = pd.read_csv("..data/curl_flexion.csv")
curl_extension = pd.read_csv("../data/curl_extension.csv")

def set_e_0(e_val):
    global e_0
    e_0 = e_val

def set_theta_0(theta_val):
    global theta_0
    theta_0 = theta_val

def init_e_0():
    global e_0
    get_encoder_value(set_e_0)

def init_theta_0():
    global theta_0
    set_theta_0(155)

def get_closest_lower_theta(input_theta):
    theta_values = curl_flextion.iloc[:, 1]
    lower_thetas = theta_values[theta_values < input_theta]

    if lower_thetas.empty:
        return None

    return lower_thetas.max()

def get_curr_e_val(theta_curr):
    return (E / 360) * (theta_curr - theta_0) + e_0



def perform_reps(start_theta):
    global no_of_reps

    start_theta_value = get_closest_lower_theta(start_theta)

    start_index = curl_flextion[curl_flextion.iloc[:, 1] == start_theta_value].index
    if start_index.empty:
        print("Start theta not found in flexion data.")
        return

    start_index = start_index[0]

    for rep in range(no_of_reps):
        print(f"\nRepetition {rep + 1}/{no_of_reps} – Flexion")

        # Flexion phase
        for i in range(start_index, len(curl_flextion)):
            theta_val = curl_flextion.iloc[i, 1]
            curr_e_val = get_curr_e_val(theta_val)
            print(f"Flexion: Theta = {theta_val}, Encoder = {curr_e_val}")
            time.sleep(0.05)

        time.sleep(2)

        print(f"\nRepetition {rep + 1}/{no_of_reps} – Extension")

        # Extension phase
        for i in range(len(curl_extension)):
            theta_val = curl_extension.iloc[i, 1]
            curr_e_val = get_curr_e_val(theta_val)
            print(f"Extension: Theta = {theta_val}, Encoder = {curr_e_val}")
            time.sleep(0.05)
