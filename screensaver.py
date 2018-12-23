# importing
import requests
import json
from tkinter import Tk, Label
import googlemaps
from datetime import datetime
import time


class App():
    def __init__(self):
        self.root = Tk()

        # decalre labels
        self.weatherLabel = Label(text="")
        self.busLabel = Label(text="")
        self.timeLabel = Label(text="")
        self.dateLabel = Label(text="")

        # packs
        self.weatherLabel.pack(expand=True)
        self.timeLabel.pack(expand=True)
        self.dateLabel.pack(expand=True)
        self.busLabel.pack(expand=True)

        # root
        self.root.title("Live Screen")
        self.root.geometry("700x300")
        self.root.attributes("-fullscreen", True)
        self.root.configure(background="black")

        # weather config
        self.weatherLabel.configure(fg="white", background="black")
        self.weatherLabel.configure(font=("Courier", 44))

        # bus config
        self.busLabel.configure(fg="white", background="black")
        self.busLabel.configure(font=("Courier", 50))

        # time config
        self.timeLabel.configure(fg="white", background="black")
        self.timeLabel.configure(font=("Courier", 150))

        # date config
        self.dateLabel.configure(fg="white", background="black")
        self.dateLabel.configure(font=("Courier", 60))

        self.update()
        self.time_update()
        self.date_update()
        self.root.mainloop()

    # update function
    def update(self):
        self.weatherLabel.configure(text=self.get_weather())
        self.busLabel.configure(text=self.get_next_bus_departure_time())
        self.root.after(5000, self.update)

    def time_update(self):
        self.timeLabel.configure(text=self.get_current_time())
        self.root.after(1000, self.time_update)

    def date_update(self):
            self.dateLabel.configure(text=self.get_current_date())
            self.root.after(60000, self.time_update)

    # returns weather
    def get_weather(self):
        print("Updating weather")
        api_key = "f5988e28703d9fdcb99201c66e8eabcf"
        city = "Kelowna"
        response = {}
        try:
            response = requests.get("http://api.openweathermap.org/data/2.5/weather?q=" + city + "&appid=" + api_key)
        except:
            print("Exception occured while getting weather.")

        res_json = json.loads(response.content.decode('utf-8'))

        current_temp = int(round(res_json["main"]["temp"] - 273.15, 0))
        current_weather = res_json["weather"][0]["main"]
        low_temp = int(res_json["main"]["temp_min"] - 273.15)
        high_temp = int(res_json["main"]["temp_max"] - 273.15)
        weather_text = "Weather: " + current_weather + ", " + str(current_temp) + " °C\n"
        low_temp_text = "Low: " + str(low_temp) + " °C\n"
        high_temp_text = "High: " + str(high_temp) + " °C"
        text = weather_text + low_temp_text + high_temp_text
        return text

    # returns current time
    def get_current_time(self):
        return datetime.now().strftime("%I:%M %p")

    # returns current time
    def get_current_date(self):
      return datetime.now().strftime('%Y-%m-%d')


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
        return "Next bus to UBCO\n" + directions_result[0]['legs'][0]['departure_time']['text']


app = App()
