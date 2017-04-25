# -*- coding: utf-8 -*-
"""
Created on Thu Nov 20 17:55:43 2014

@author: lrousmaniere
"""

"""
This is a command line script to print accesses above a specific collection
elevation threshold, forward a specified number of days (on any SkySat)
"""

from pyorbital.orbital import Orbital
import math
import Haversine
import datetime, csv

collection_elevation_threshold = int(raw_input("Min Collection Elevation: "))
days_forward = raw_input("Days ahead: ")
test_target = [37.77493, -122.419416]

skysats = ["SKYSAT-1", "SKYSAT-2", "SKYSAT-C1", "SKYSAT-C2", "SKYSAT-C3", "SKYSAT-C4", "SKYSAT-C5"]
start = (datetime.datetime.today() + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0) #for tomorrow's points
end = (datetime.datetime.today() + datetime.timedelta(days=int(days_forward))).replace(hour=0, minute=0, second=0, microsecond=0)
print "\nStart: " + str(start.date())
print "End: " + str(end.date())

## For the input 'satellite', create a list of lat/lons for every increment (below) number of seconds
## that the satellite is in a descending, lit orbit; between the above start and end dates.
def generate_points_per_satellite(satellite, start, end):
    orb = Orbital(satellite)
    satellite_lat_lons = []
    increment_in_minutes = 0.083 #Every 5 seconds
    increment = datetime.timedelta(minutes=float(increment_in_minutes))
    list_of_dates = []

    while start < end:
        cd = str(start.date())
        if cd not in list_of_dates:
            list_of_dates.append(cd)
        lon, lat, alt = orb.get_lonlatalt(start)
        satellite_lat_lons.append([lat, lon, alt, str(start)])
        start += increment
    
    light_list = []
    for j in range((len(satellite_lat_lons))-1):
        if satellite_lat_lons[j][0] >= satellite_lat_lons[j+1][0]:
            light_list.append(satellite_lat_lons[j])

    return light_list, list_of_dates

## Calculate the collection elevation (NOT off Nadir) for every lat/lon point given in the above
## generate_points_per_satellite function. The increment_in_minutes var impacts compute time
def calculate_collection_elevation(target_lat, target_lon, sat_lat, sat_lon, sat_alt):
    ground_distance = Haversine.distance((target_lat, target_lon), (sat_lat, sat_lon))
    collection_elevation = math.degrees( (math.atan(sat_alt / ground_distance)))
    return collection_elevation

def calculate_time_in_access_and_max_el(satellite_lat_lons, date_list):
    time_in_access = 0
    start_collection_time = ""
    max_day_elevation = 0
    date_list_dict = {}
    for dates in date_list: #create dictionary for all dates between start and end dates
        date_list_dict[dates] = ""
    for satellite_lat_lon in satellite_lat_lons:
        target_lat = float(test_target[0])
        target_lon = float(test_target[1])
        sat_lat = float(satellite_lat_lon[0])
        sat_lon = float(satellite_lat_lon[1])
        sat_alt = float(satellite_lat_lon[2])
        date = satellite_lat_lon[-1].split(" ")[0]
        dateWtime = satellite_lat_lon[-1]
        collection_elevation = calculate_collection_elevation(target_lat, target_lon, sat_lat, sat_lon, sat_alt)

        ## Find all times when collection_elevation is higher than threshold set up top
        start_end_value = 0
        if collection_elevation > collection_elevation_threshold:
            if start_end_value == 0:
                start_collection_time = dateWtime
                start_end_value += 1
            if collection_elevation > max_day_elevation:
                max_day_elevation = collection_elevation
            time_in_access += 5
            date_list_dict[date] = [round(max_day_elevation, 3), time_in_access, start_collection_time]
            # print str(dateWtime), "El = " + str(collection_elevation)
        else:
            time_in_access = 0
            max_day_elevation = 0
            start_end_value = 0
    ## date_list_dict = max_day_elevation, time_in_access, start_collection_time
    return date_list_dict

def main():
    print "Target: " + str(test_target[0]) +", " + str(test_target[1]) +"\n...."
    #satellite_lat_lons, date_list = generate_points_per_satellite(satellite, start, end) #returns lat,lon,alt,star every 15 sec
    #date_list_dict = calculate_time_in_access_and_max_el(satellite_lat_lons, date_list)

    big_list_of_accesses = []

    for sat_name in skysats:
        satellite_lat_lons, date_list = generate_points_per_satellite(sat_name, start, end)
        date_list_dict = calculate_time_in_access_and_max_el(satellite_lat_lons, date_list)
        big_list_of_accesses.append([str(sat_name), date_list_dict])

    data_as_list = []
    for data in big_list_of_accesses:
        satellite = data[0]
        data_dict = data[1]
        for date,values in data_dict.iteritems():
            try:
                #Append max_day_elevation, time_in_access, start_collection_time
                data_as_list.append([date, values[0], values[1], values[2], satellite])
            except: pass
    data_as_list.sort(key=lambda r:r[3]) #sort by values[2] (datetime)

    f = open('Access_report_anySatellite.csv', 'wb')
    writer = csv.writer(f)
    writer.writerow(['Date', 'MaxEl', 'DurationS', 'Start', 'End', 'Satellite'])
    for i in data_as_list:
        startAsDatetime = datetime.datetime.strptime(i[3], '%Y-%m-%d %H:%M:%S.%f')
        endAsDatetime = startAsDatetime + datetime.timedelta(seconds=i[2])
        startTimeFormat= datetime.datetime.strftime(startAsDatetime, '%Y-%m-%dT%H:%M:%SZ')
        endTimeFormat = datetime.datetime.strftime(endAsDatetime, '%Y-%m-%dT%H:%M:%SZ')
        writer.writerow([i[0], i[1], i[2], startTimeFormat, endTimeFormat, i[4]])
        print i[0], i[1], i[2], startTimeFormat, endTimeFormat, i[4]

if __name__ == "__main__":
    main()
