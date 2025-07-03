import pandas as pd
import sqlite3
import numpy as np
import time
import os
from service.arduino_comm import get_encoder_value

_db_initialized = False

initial_encoder_value=0
curr_angle=0
number_of_reps=1

BASE_DIR = ""
A_MATRICES_PATH = ""

db_conn = None

last_states=[60.90983284206268, 61.12161056629257, 61.332797560605094, 61.54373428281216, 61.75394691218596]

def init_db():
    global _db_initialized
    if not _db_initialized:
        global BASE_DIR
        global A_MATRICES_PATH
        global db_conn

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        A_MATRICES_PATH = os.path.join(BASE_DIR, 'data', 'A_matrices.db')

        db_conn = sqlite3.connect(A_MATRICES_PATH)

        _db_initialized = True

def init_enc_value():
    global initial_encoder_value
    get_encoder_value(set_initial_encoder_value)


def ensure_db(func):
    def wrapper(*args, **kwargs):
        init_db()
        return func(*args, **kwargs)
    return wrapper


def set_initial_encoder_value(encoder_value):
    global initial_encoder_value
    initial_encoder_value=encoder_value

def update_curr_angle(callback=None):
    get_encoder_value(lambda enc_val: set_curr_angle(enc_val, callback))

def set_curr_angle(curr_encoder_value, callback):
    global curr_angle
    theta = 20    # initialize values
    pulse = 100   # initialize values

    curr_angle = (curr_encoder_value - initial_encoder_value) * (theta / pulse) + 155

    if callback:
        callback(curr_angle)

def get_curr_angle():
    global curr_angle
    return curr_angle

def set_number_of_reps(reps):
    global number_of_reps
    number_of_reps=reps

def exercise_loop(encorder_curr_angle,direction):

    get_state_matrix_A_and_curr_angle=assign_state(encorder_curr_angle,direction)

    state_matrix_A=get_state_matrix_A_and_curr_angle[0]
    
    theta_now = get_state_matrix_A_and_curr_angle[1]

    theta_prev = last_states[-1]
    
    state_vector_X = build_state_vector(theta_now, theta_prev)
    
    estimated_next_angle=compute_next_state(state_matrix_A, state_vector_X)[0]
    update_last_states(estimated_next_angle)
    
    return estimated_next_angle

def update_last_states(new_theta, max_size=5):
   
    global last_states
    if len(last_states) >= max_size:
        last_states.pop(0)
    last_states.append(new_theta)

def build_state_vector(theta_now, theta_prev):
    dt = 0.01  # Fixed time step
    theta_now = float(theta_now)
    theta_prev = float(theta_prev)

    theta_dot = float((theta_now - theta_prev) / dt)
    return np.array([[theta_now], [theta_dot]])


def compute_next_state(A_matrix, current_state):

    return A_matrix @ current_state


@ensure_db
def get_lower_A_matrix(given_theta, phase):
    global db_conn
    # Step 1: Connect and load only theta + index
    df = pd.read_sql_query(
        "SELECT step_index, theta FROM full_theta_with_A WHERE dataset_name = ? ORDER BY theta ASC",
        db_conn, params=(phase,)
    )

    # Step 2: Find bounds
    lower_index = None
    for i in range(len(df) - 1):
        theta1 = df.iloc[i]['theta']
        theta2 = df.iloc[i + 1]['theta']
        if theta1 <= given_theta < theta2:
            if phase=="curl_flexion":
                lower_index = int(df.iloc[i]['step_index'])-1
            else:
                lower_index=int(df.iloc[i]['step_index'])
            break
    cursor = db_conn.cursor()

    # Step 3: Handle out-of-range → return 2x2 zero matrix
    if lower_index is None:
        return {
            "matched_theta": given_theta,
            "step_index": -1,
            "A_matrix": np.zeros((2, 2)),
            "current_theta": given_theta # meka wenas karanna!!!!!!!!!!!  
        }

    # Step 4: Fetch corresponding 2x2 A matrix
    A_query = """
    SELECT theta, a11, a12,
                  a21, a22
    FROM full_theta_with_A
    WHERE dataset_name = ? AND step_index = ?
    """
    cursor.execute(A_query, (phase, lower_index))
    row = cursor.fetchone()

    theta_value = row[0]
    A_matrix = np.array(row[1:]).reshape(2, 2)
    print(A_matrix)

    return {
        "matched_theta": df[df['step_index'] == lower_index]['theta'].values[0],
        "step_index": lower_index,
        "A_matrix": A_matrix,
        "current_theta": theta_value
    }

def direction(past_angles):

    diffs = [past_angles[i+1] - past_angles[i] for i in range(len(past_angles)-1)]

    avg_diff = sum(diffs) / len(diffs)
    #print(avg_diff)
    if avg_diff > 0.1:
        return 1
    elif avg_diff < -0.1:
        return -1
    else:
        return 0

def assign_state(state,dir):
    if dir>0:
        result = get_lower_A_matrix(state, "curl_extension")
        return [result['A_matrix'],result['current_theta']]

    elif dir<0:
        result = get_lower_A_matrix(state, "curl_flexion")
        return [result['A_matrix'],result['current_theta']]
    else:
        pass


def run_exercise():
    global number_of_reps
    global curr_angle
    global last_states

    for i in range(number_of_reps):
        print(f"Repetition {i + 1}/{number_of_reps} – Flexion")

        while True:
            update_curr_angle()  # Blocking read
            time.sleep(0.01)

            dir_val = direction(last_states) if len(last_states) > 5 else -1

            if dir_val != 0:
                est_angle = exercise_loop(curr_angle, dir_val)
                print(f"→ Estimated Angle: {float(est_angle):.2f}")
            else:
                break

        time.sleep(0.8)
        last_states = [curr_angle] * 5

        print(f"Repetition {i + 1}/{number_of_reps} – Extension")

        while True:
            update_curr_angle()
            time.sleep(0.01)

            dir_val = direction(last_states) if len(last_states) > 5 else 1

            if dir_val != 0:
                est_angle = exercise_loop(curr_angle, dir_val)
                print(f"→ Estimated Angle: {float(est_angle):.2f}")
            else:
                break

        time.sleep(0.8)