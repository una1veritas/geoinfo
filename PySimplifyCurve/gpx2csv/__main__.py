'''
Created on 2025/07/27

@author: sin
'''

import gpxpy
import gpxpy.gpx
import csv

if __name__ == '__main__':

    # Open the GPX file
    with open('2023-06-22 16_48_37.gpx', 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    # Prepare data for CSV
    data_rows = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                data_rows.append({
                    'latitude': point.latitude,
                    'longitude': point.longitude,
                    'elevation': point.elevation,
                    'time': point.time.isoformat() if point.time else None
                })

    # Write to CSV
    if data_rows:
        with open('output.csv', 'w', newline='') as csvfile:
            fieldnames = data_rows[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data_rows)
