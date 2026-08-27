'''
Created on 2025/07/27

@author: sin
'''
import sys
import gpxpy.gpx
import csv

if __name__ == '__main__':
    filename = '2025-0726-151032.gpx'  #default file name
    if len(sys.argv) > 1 : filename = sys.argv[1]
    if filename == None :
        raise ValueError('no input .gpx file name.')
    
    # Open the GPX file
    print(f'open file \'{filename}\'.')
    with open(filename, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    # Prepare data for CSV
    data_rows = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                data_rows.add({
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
        print(f'written to \'output.csv\'.')
