import requests
import json
from tkinter import Tk, Label
import googlemaps
from datetime import datetime


class App():
    def __init__(self):
        self.root = Tk()
        self.label = Label(text="")
        self.label.pack(expand=True)
        self.root.title("Screensaver")
        self.root.geometry("700x300")
        self.root.attributes("-fullscreen", True)
        self.root.configure(background="black")
        self.label.configure(fg="white", background="black")
        self.label.configure(font=("Courier", 44))
        self.update_weather()
        self.root.mainloop()

    def update_weather(self):
        self.get_weather()
        self.root.after(5000, self.update_weather)

    def get_weather(self):
        print("Updating weather")
        api_key = "f5988e28703d9fdcb99201c66e8eabcf"
        city = "Kelowna"
        response = requests.get("http://api.openweathermap.org/data/2.5/weather?q=" + city + "&appid=" + api_key)

        res_json = json.loads(response.content.decode('utf-8'))

        current_temp = int(round(res_json["main"]["temp"] - 273.15, 0))
        current_weather = res_json["weather"][0]["main"]
        low_temp = int(res_json["main"]["temp_min"] - 273.15)
        high_temp = int(res_json["main"]["temp_max"] - 273.15)
        weather_text = "Weather: " + current_weather + ", " + str(current_temp) + " °C\n"
        low_temp_text = "Low: " + str(low_temp) + " °C\n"
        high_temp_text = "High: " + str(high_temp) + " °C"
        text = weather_text + low_temp_text + high_temp_text
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

      

app = App()