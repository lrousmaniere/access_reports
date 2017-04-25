# -*- coding: utf-8 -*-
"""
Created on Thu Nov 20 17:55:43 2014

@author: lrousmaniere
"""

"""
This is a command line script to determine if we have upcoming access (tomorrow) to the 
input lat/lon on any of the satellites in the skysat list below
"""

from pyorbital.orbital import Orbital
import math
import Haversine
import datetime, csv

input_lat = raw_input("Latitude: ")
input_lon = raw_input("Longitude: ")

input_latlon = [float(input_lat), float(input_lon)]

skysats = ["SKYSAT-1", "SKYSAT-2", "SKYSAT-C1", "SKYSAT-C2", "SKYSAT-C3", "SKYSAT-C4", "SKYSAT-C5"]
start = (datetime.datetime.today() + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0) #for tomorrow's points
end = (datetime.datetime.today() + datetime.timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
print "\nCalculating...       " + str(start)+" to "+str(end) + "\n"

def generate_points_per_satellite(satellite, start, end):
    orb = Orbital(satellite)
    point_list = []
    increment_in_minutes = 0.25
    increment = datetime.timedelta(minutes=float(increment_in_minutes))

    while start < end:
        lon, lat, alt = orb.get_lonlatalt(start)
        point_list.append([lat, lon, alt, str(start)])
        start += increment
    
    light_list = []
    for j in range((len(point_list))-1):
        if point_list[j][0] >= point_list[j+1][0]:
            light_list.append(point_list[j])

    return light_list

def calculate_collection_elevation(target_lat, target_lon, sat_lat, sat_lon, sat_alt):
    ground_distance = Haversine.distance((target_lat, target_lon), (sat_lat, sat_lon))
    collection_elevation = math.degrees( (math.atan(sat_alt / ground_distance)))
    return collection_elevation

def build_only_dark_points(point_list):
    dark_list = []    
    for i in range((len(point_list))-1):
        if point_list[i][0] <= point_list[i+1][0]:
            dark_list.append(point_list[i])    
    return dark_list
        
def create_csv(point_list):    
    csv_name = "Tomorrows_access.csv"
    f = open(csv_name,'wb')
    writer = csv.writer(f)
    writer.writerow(["count","lat","long","time"])
    for row in point_list:
        writer.writerow([row[0],row[1],row[2],row[3]])
                
def main():
    print "target: " + str(input_latlon[0]) + ", " + str(input_latlon[1]) + "\n"
    for satellites in skysats:
        point_list = generate_points_per_satellite(satellites, start, end)
        end_point = len(point_list)
        i = 0
        highest_elevation = 0
        time_at_highest_elevation = ""
        for satellite_lat_lon in point_list:
            target_lat = float(input_latlon[0])
            target_lon = float(input_latlon[1])
            sat_lat = float(satellite_lat_lon[0])
            sat_lon = float(satellite_lat_lon[1])
            sat_alt = float(satellite_lat_lon[2])
            collection_elevation = calculate_collection_elevation(target_lat, target_lon, sat_lat, sat_lon, sat_alt)
            if collection_elevation > highest_elevation:
                highest_elevation = round(collection_elevation, 2)
                time_at_highest_elevation = satellite_lat_lon[-1]
            if i == end_point - 1:
                print str(satellites) + " best access at (CE): " + str(highest_elevation) + " degrees at " + time_at_highest_elevation + "\n"
            i += 1
    #create_csv(point_list)
    
if __name__ == "__main__":
    main()
