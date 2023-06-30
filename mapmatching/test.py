import glob
import pandas as pd
import ast
import folium
import os
from pathlib import Path
import math
from geopy.distance import great_circle

csv_files = glob.glob("matched_path/paths_info_2023-06-10 22_33_53_*.csv")
gps_traj = pd.read_csv('MyTracks/2023-06-03 13_37_21.csv')

dataframes = [pd.read_csv(f) for f in csv_files]

df = pd.concat(dataframes, ignore_index=True)

m = folium.Map(location=[33.5953052 ,130.3574264], tiles='cartodbpositron', zoom_start=20)

extracted_dataframes = []

BETA=4.07
SIGMA_Z=3
MINIMUM=10**(-45)
MIN=10 ** (-95)

def calculate_emission_probability(traj, matched_pos):
        c = 1 / (SIGMA_Z * math.sqrt(2 * math.pi))
        a=great_circle((traj[0],traj[1]), (matched_pos[0],matched_pos[1])).m
        emiprob=c * math.exp(-a**2)
        return emiprob


for df in dataframes:
    temp_data = []
    read_flag = False

    for _, row in df.iterrows():
        if row['prob'] == 'Path1':
            read_flag = True

        if row['prob'] == 'Path2':
            read_flag = False
            if temp_data:
                temp_df = pd.concat(temp_data, axis=1).T
                extracted_dataframes.append(temp_df)
                temp_data = []

            for ind, r in temp_df.iterrows():
                    # Parse the 'traj' and 'matched_position_on_current_edge' fields
                    if ind==0: continue
                    traj = ast.literal_eval(r['traj'])
                    matched_pos = ast.literal_eval(r['matched_position_on_current_edge'])
                    prob=calculate_emission_probability(traj, matched_pos)
                    print(prob)
                    
                    folium.CircleMarker(traj, popup=('traj:',ind,"prob:",prob), radius=1.8,color="purple",fill=True,fill_opacity=1,fill_color="purple").add_to(m)
                    folium.CircleMarker(matched_pos, popup=('matched pos:',ind,"prob:",prob), radius=1.8,color="red",fill=True,fill_opacity=1,fill_color="red").add_to(m)


        if read_flag:
            temp_data.append(row)
"""
if temp_data:
    temp_df = pd.concat(temp_data, axis=1).T
    extracted_dataframes.append(temp_df)

    for _, r in temp_df.iterrows():
        # Parse the 'traj' and 'matched_position_on_current_edge' fields
        traj = ast.literal_eval(r['traj'])
        matched_pos = ast.literal_eval(r['matched_position_on_current_edge'])
        prob=calculate_emission_probability(traj, matched_pos)
        print(prob)

        # Add markers for 'traj' and 'matched_position_on_current_edge'
        folium.CircleMarker(traj, popup=('traj',ind), radius=1.8,fill=True,color="purple",fill_opacity=1,fill_color="purple").add_to(m)
        folium.CircleMarker(matched_pos, popup=('matched pos',ind),radius=1.8,color="red",fill=True,fill_opacity=1,fill_color="red").add_to(m)
"""




input_file_path = "matched_point/2023-06-10 22_33_53.html"
m.save(input_file_path)
