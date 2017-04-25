# -*- coding: utf-8 -*-
"""
Created on Thu Nov 20 17:55:43 2014

@author: lrousmaniere
"""

"""
This is a command line script to print accesses on a single SkySat
above a specified collection elevation, forward X number of days

*Note, current target is hardcoded in script, will need to update there
"""

from pyorbital.orbital import Orbital
import math
import Haversine
import datetime, csv

collection_elevation_threshold = int(raw_input("Min Collection Elevation: "))
days_forward = raw_input("Days ahead: ")
satellite = raw_input("Satellite (i.e. SKYSAT-C2): ")
test_target = [37.77493, -122.419416]

start = (datetime.datetime.today() + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0) #for tomorrow's points
end = (datetime.datetime.today() + datetime.timedelta(days=int(days_forward))).replace(hour=0, minute=0, second=0, microsecond=0)
print "\nStart: " + str(start.date())
print "End: " + str(end.date())

def generate_points_per_satellite(satellite, start, end):
    orb = Orbital(satellite)
    point_list = []
    increment_in_minutes = 0.083 #Every 5 seconds
    increment = datetime.timedelta(minutes=float(increment_in_minutes))
    list_of_dates = []

    while start < end:
        cd = str(start.date())
        if cd not in list_of_dates:
            list_of_dates.append(cd)
        lon, lat, alt = orb.get_lonlatalt(start)
        point_list.append([lat, lon, alt, str(start)])
        start += increment
    
    light_list = []
    for j in range((len(point_list))-1):
        if point_list[j][0] >= point_list[j+1][0]:
            light_list.append(point_list[j])

    return light_list, list_of_dates

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

def main():
    print "Satellite: " + str(satellite)
    print "Target: " + str(test_target[0]) +", " + str(test_target[1]) +"\n...."
    point_list, date_list = generate_points_per_satellite(satellite, start, end) #returns lat,lon,alt,star every 15 sec
    time_in_access = 0 #in seconds
    #end_point = len(point_list)
    #i = 0
    #highest_elevation = 0
    max_day_elevation = 0
    start_collection_time = ""
    end_collection_time = ""
    date_list_dict = {}
    for dates in date_list:
        date_list_dict[dates] = ""
    #append date_list_dict with the highest_elevation and time
    for satellite_lat_lon in point_list:

        target_lat = float(test_target[0])
        target_lon = float(test_target[1])
        sat_lat = float(satellite_lat_lon[0])
        sat_lon = float(satellite_lat_lon[1])
        sat_alt = float(satellite_lat_lon[2])
        date = satellite_lat_lon[-1].split(" ")[0]
        dateWtime = satellite_lat_lon[-1]
        collection_elevation = calculate_collection_elevation(target_lat, target_lon, sat_lat, sat_lon, sat_alt)

        #IF collection_elevation > 56 degrees, create access, add time
        start_end_value = 0
        if collection_elevation > collection_elevation_threshold:
            if start_end_value == 0:
                start_collection_time = dateWtime
                start_end_value += 1
            if collection_elevation > max_day_elevation:
                max_day_elevation = collection_elevation
            time_in_access += 5
            date_list_dict[date] = [round(max_day_elevation, 3), time_in_access, start_collection_time]
            #print str(dateWtime), "El = " + str(collection_elevation)
        else:
            time_in_access = 0
            max_day_elevation = 0
            start_end_value = 0

    #Create CSV
    f = open('Access_report_%s.csv'%str(satellite), 'wb')
    writer = csv.writer(f)
    writer.writerow(['Date', 'MaxEl', 'Duration_s', 'StartUTC', 'EndUTC'])
    for lines in date_list_dict.iteritems():
        try:
            duration = lines[1][1]
            start_time = datetime.datetime.strptime(lines[1][2], "%Y-%m-%d %H:%M:%S.%f")
            end_time = start_time + datetime.timedelta(seconds=duration)
            start_time_iso = datetime.datetime.strftime(start_time, "%Y-%m-%dT%H:%M:%SZ")
            end_time_iso = datetime.datetime.strftime(end_time, "%Y-%m-%dT%H:%M:%SZ")
            print lines[0], lines[1][0], duration, start_time_iso, end_time_iso
            writer.writerow([lines[0], lines[1][0], duration, start_time_iso, end_time_iso])
        except:continue
    print "Done!"

if __name__ == "__main__":
    main()
