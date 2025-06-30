import pandas as pd
import sqlite3
import numpy as np
import time


#read the following inputs from the board
encorder_curr_angle=62
number_of_reps=6


# Read the first sheet
ds_curl_flexion = pd.read_csv('../data/generalized_curl_flexion.csv')
ds_curl_extension = pd.read_csv('../data/generalized_curl_extension.csv')
a_matrices_path = '../data/A_matrices.db'

last_states=[60.90983284206268, 61.12161056629257, 61.332797560605094, 61.54373428281216, 61.75394691218596]
initial_encoder_value=12.5

def Encoder_angle_initialization(curr_encoder_value):
    initial_encoder_value=curr_encoder_value

def curr_angle(curr_encoder_value):
    theta=20 #initialize these two values pakoo
    pulse=100 #initialize these two values pakoo
    calculated_current_angle=(curr_encoder_value-initial_encoder_value)*(theta/pulse)+155

def exersice_loop(encorder_curr_angle,direction):

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
    theta_dot = (theta_now - theta_prev) / dt
    return np.array([[theta_now], [theta_dot]])


def compute_next_state(A_matrix, current_state):

    return A_matrix @ current_state


def get_lower_A_matrix(given_theta, phase):
    # Step 1: Connect and load only theta + index
    conn = sqlite3.connect(a_matrices_path)
    df = pd.read_sql_query(
        "SELECT step_index, theta FROM full_theta_with_A WHERE dataset_name = ? ORDER BY theta ASC",
        conn, params=(phase,)
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
    cursor = conn.cursor()

    # Step 3: Handle out-of-range → return 2x2 zero matrix
    if lower_index is None:
        conn.close()
        return {
            "matched_theta": given_theta,
            "step_index": -1,
            "A_matrix": np.zeros((2, 2))
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
    conn.close()

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



if __name__ == "__main__":
    for i in range(0,number_of_reps):
        encorder_curr_angle=62
        while True:
            if len(last_states)<=5:
                direction=-1
            else:
                direction(last_states)
            
            if direction!=0:
                exersice_loop(encorder_curr_angle,direction)
            else:
                break
        
        # sleeping time between the phase change

        time.sleep(0.8)
        
        last_states=[]

        while True:
            if len(last_states)<=5:
                direction=1
            else:
                direction(last_states)
            
            if direction!=0:
                exersice_loop(encorder_curr_angle,direction)
            else:
                break

        time.sleep(0.8)