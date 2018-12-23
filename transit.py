from tkinter import *
import googlemaps
from datetime import datetime

#
# Returns the next bus departure time as a string.
# From the Artium Student Residence to UBCO.
# Next bus time relies on current time.
#
def get_next_bus_departure_time():

    # Initialize Google Maps API.
    gmaps = googlemaps.Client(key='AIzaSyCZ_3BKxqS5_SS41sUchUUfd6Sq4jiY6-A')

    # Request directions via public transit.
    now = datetime.now()
    directions_result = gmaps.directions("The Artium Student Residence, Kelowna",
                                         "UBC Okanagan, Kelowna, BC",
                                         mode="transit",
                                         departure_time=now)

    # Retrieve departure time and return string.
    return next_bus_time = directions_result[0]['legs'][0]['departure_time']['text']
