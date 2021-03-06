# extract_bikeshare_data.py

import code # to debug: `code.interact(local=locals())`
import os
from pprint import pprint
import pybikes
import json
import csv

networks_dot_csv = os.path.join(os.path.dirname(__file__), "data/networks.csv")
print "WRITING TO CSV FILE -- %(file_name)s" % {"file_name": networks_dot_csv}
os.remove(networks_dot_csv) if os.path.isfile(networks_dot_csv) else "NO CSV FILE DETECTED"
networks_csv = csv.writer(open(networks_dot_csv, "w"), lineterminator=os.linesep)
networks_csv.writerow(["tag", "name", "city", "country", "company", "longitude", "latitude", "feed_url", "feed_format", "system_type"])

network_companies_dot_csv = os.path.join(os.path.dirname(__file__), "data/network_companies.csv")
print "WRITING TO CSV FILE -- %(file_name)s" % {"file_name": network_companies_dot_csv}
os.remove(network_companies_dot_csv) if os.path.isfile(network_companies_dot_csv) else "NO CSV FILE DETECTED"
network_companies_csv = csv.writer(open(network_companies_dot_csv, "w"), lineterminator=os.linesep)
network_companies_csv.writerow(["network_tag","company_name"])

stations_dot_csv = os.path.join(os.path.dirname(__file__), "data/stations.csv")
print "WRITING TO CSV FILE -- %(file_name)s" % {"file_name": stations_dot_csv}
os.remove(stations_dot_csv) if os.path.isfile(stations_dot_csv) else "NO CSV FILE DETECTED"
stations_csv = csv.writer(open(stations_dot_csv, "w"), lineterminator=os.linesep)
stations_csv.writerow(["id","network_tag","name","latitude","longitude","bikes","free","timestamp","extra"])

def list_of_encoded_strings(array_of_unicode_strings):
    new_list = []
    for str in array_of_unicode_strings:
        new_list.append(str.encode())
    return new_list

#
# PARSE KNOWN NETWORKS FROM FILE
#

networks_dot_json = os.path.join(os.path.dirname(__file__), "fixtures/citybikes_api/get_networks.json")
with open(networks_dot_json) as json_file:
    station_id = 0
    known_networks = json.load(json_file)
    for known_network in known_networks:
        network_tag = known_network["tag"].encode()

        #
        # GET NETWORK .JSON
        #

        try:
            response = pybikes.get(network_tag)
        except:
            continue # workaround for `Exception: System Cyclocity needs a key to work`

        try:
            network_city_name = response.meta["city"].encode()
        except UnicodeEncodeError:
            network_city_name = "#UNENCODABLE"

        try:
            network_name = response.meta["name"].encode()
        except UnicodeEncodeError:
            network_name = "#UNENCODABLE"
        except UnicodeDecodeError:
            network_name = "#UNDECODABLE"

        try:
            feed_url = response.feed_url
        except:
            feed_url = None

        try:
            feed_format = response.method.encode()
        except:
            feed_format = None

        try:
            system_type = response.meta["system"].encode()
        except:
            system_type = None

        network = {
            'tag': response.tag.encode(),
            'name': network_name,
            'city': network_city_name,
            'country': response.meta["country"].encode(),
            'company': response.meta["company"],
            'longitude': response.meta["longitude"],
            'latitude':response.meta["latitude"],
            'feed_url': feed_url,
            'feed_format': feed_format,
            'system_type': system_type,
        }
        pprint(network)

        #
        # WRITE NETWORK .CSV
        #

        networks_csv.writerow([network["tag"], network["name"], network["city"], network["country"], network["company"], network["longitude"], network["latitude"], network["feed_url"], network["feed_format"], network["system_type"] ])

        #
        # WRITE NETWORK COMPANIES .CSV
        #

        company = response.meta["company"]
        if type(company) == str:
            network_companies = [company] # convert to array of one element
        elif company == None:
            print "no companies" # network_companies = [] # convert to empty array
        elif type(company) == list:
            network_companies = list_of_encoded_strings(company) # convert each array element
        else:
            code.interact(local=locals())

        for company_name in network_companies:
            network_companies_csv.writerow([network["tag"], company_name])

        #
        # GET NETWORK STATIONS .JSON
        #

        try:
            response.update()
        except:
            continue # skip problematic calls for: ["bicipalma", et al]

        print len(response.stations)

        for station in response.stations:
            station_id +=1
            # print station_id # pprint(station.to_json())

            try:
                timestamp = station.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            except:
                timestamp = None # handle stations like the 'bike-sharing-napoli' network's "CleaNap demo LumiLab" station, which has no timestamp

            try:
                station_name = station.name.encode()
            except:
                station_name = None

            #
            # WRITE NETWORK STATIONS .CSV
            #

            stations_csv.writerow([station_id, network["tag"], station_name, station.latitude, station.longitude, station.bikes, station.free, timestamp, station.extra ])
