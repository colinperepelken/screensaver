import requests
import json
from tkinter import *
import googlemaps
from datetime import datetime


class App():
    def __init__(self):
        self.root = Tk()
        self.label = Label(text="")
        self.label.pack()
        self.root.title("Weather")
        self.root.geometry("700x300")
        self.update_weather()
        self.root.mainloop()

    def update_weather(self):
        self.get_weather()
        self.root.after(1000, self.update_weather)

    def get_weather(self):
      print("Updating weather")
      api_key = "f5988e28703d9fdcb99201c66e8eabcf"
      city = "Kelowna"
      response = requests.get("http://api.openweathermap.org/data/2.5/weather?q=" + city + "&appid=" + api_key)

      res_json = json.loads(response.content.decode('utf-8'))

      weather = "Weather: " + res_json["weather"][0]["main"] + "\n"
      low_temp = "Low: " + str(res_json["main"]["temp_min"] - 273.15)  + "\n"
      high_temp = "High: " + str(res_json["main"]["temp_max"] - 273.15)
      text = weather + low_temp + high_temp
      self.label.configure(text=text + "\nNext bus: " + self.get_next_bus_departure_time())

    #
    # Returns the next bus departure time as a string.
    # From the Artium Student Residence to UBCO.
    # Next bus time relies on current time.
    #
    def get_next_bus_departure_time(self):

        # Initialize Google Maps API.
        gmaps = googlemaps.Client(key='AIzaSyCZ_3BKxqS5_SS41sUchUUfd6Sq4jiY6-A')

        # Request directions via public transit.
        now = datetime.now()
        directions_result = gmaps.directions("The Artium Student Residence, Kelowna",
                                            "UBC Okanagan, Kelowna, BC",
                                            mode="transit",
                                            departure_time=now)

        # Retrieve departure time and return string.
        return directions_result[0]['legs'][0]['departure_time']['text']

      

app=App()