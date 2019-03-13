# importing
import requests
import json
from tkinter import *
import googlemaps
from datetime import datetime
from PIL import Image, ImageTk
import yaml
from unsplash.api import Api
from unsplash.auth import Auth

class App():
    def __init__(self):

        # Initialize global config file.
        self.config = yaml.safe_load(open("config.yml"))

        # Initialize Google Maps API.
        self.gmaps = googlemaps.Client(key=self.config['google_maps_api_key'])

        # Init Unsplash.
        auth = Auth(self.config['unsplash_settings']['client_id'],
                    self.config['unsplash_settings']['client_secret'],
                    self.config['unsplash_settings']['redirect_uri'],
                    code="")
        api = Api(auth)

        # Use a session for requests.
        self.session = requests.Session()
        self.root = Tk()

        # Initialize background image.
        randomImage = api.photo.random(orientation="landscape", featured=True)
        self.backgroundImage = PhotoImage(randomImage)
        print(type(self.backgroundImage))
        self.backgroundLabel = Label(image=self.backgroundImage)
        self.backgroundLabel.image = self.backgroundImage # to prevent garbage colletion from destroying image.
        self.backgroundLabel.place(x=0, y=0, relwidth=1, relheight=1)


        self.weatherFrame = Frame(self.root, bg="black")

        # Init labels.
        self.weatherLabel = Label(self.weatherFrame, text="")
        self.weatherIcon = Label(self.weatherFrame, borderwidth=0)

        self.busLabel = Label(text="")
        self.timeLabel = Label(text="")
        self.dateLabel = Label(text="")
        self.backgroundImage = Label(text="")

        # Set layouts.
        self.weatherFrame.pack(side=TOP, pady=50)
        self.weatherLabel.pack(side=LEFT, fill=NONE)
        self.weatherIcon.pack(side=LEFT, fill=NONE)
        self.timeLabel.pack(expand=True)
        self.dateLabel.pack(expand=True)
        self.busLabel.pack(pady=50)

        # Set window attributees.
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
        try:
          self.weatherLabel.configure(text=self.get_weather())
        except Exception as e:
          print("Exception occured while getting weather: " + str(e))
        try:
            print("skipping bus...")
          # self.busLabel.configure(text=self.get_next_bus_departure_time())
        except Exception as e:
          print("Exception occured while getting next bus departure time: " + str(e))
        self.root.after(5000, self.update)

    def time_update(self):
        self.timeLabel.configure(text=self.get_current_time())
        self.root.after(1000, self.time_update)

    def date_update(self):
            self.dateLabel.configure(text=self.get_current_date())
            self.root.after(60000, self.time_update)

    # returns weather
    def get_weather(self):
        print("Updating weather...")
        api_key = self.config['weather_settings']['openweather_api_key']
        city = self.config['weather_settings']['city']

        response = self.session.get("http://api.openweathermap.org/data/2.5/weather?q=" + city + "&appid=" + api_key)
        res_json = json.loads(response.content.decode('utf-8'))

        current_temp = int(round(res_json["main"]["temp"] - 273.15, 0))
        current_weather = res_json["weather"][0]["main"]


        image = Image.open(self.get_weather_icon(current_weather))
        image = image.resize((100, 100), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(image=image)

        self.weatherIcon.configure(image=photo)
        self.weatherIcon.image = photo


        low_temp = int(res_json["main"]["temp_min"] - 273.15)
        high_temp = int(res_json["main"]["temp_max"] - 273.15)
        weather_text = "Weather: " + current_weather + ", " + str(current_temp) + " °C\n"
        low_temp_text = "Low: " + str(low_temp) + " °C\n"
        high_temp_text = "High: " + str(high_temp) + " °C"
        text = weather_text + low_temp_text + high_temp_text
        return text

    def get_weather_icon(self, weather):
        icon_map = {
          "Clouds": "images/cloudy.png",
          "Snow": "images/snow.png",
          "Rain": "images/rain.png"
        }

        return icon_map[weather]

    # returns current time
    def get_current_time(self):
        return datetime.now().strftime("%I:%M %p")

    # returns current time
    def get_current_date(self):
      return datetime.now().strftime('%Y-%m-%d')


    # Returns the next bus departure time as a string.
    # From the Artium Student Residence to UBCO.
    # Next bus time relies on current time.
    def get_next_bus_departure_time(self):
        print("Updating bus departure time...")
        # Request directions via public transit.
        now = datetime.now()
        directions_result = self.gmaps.directions(self.config['transit_settings']['home_location'],
                                                  self.config['transit_settings']['destination_location'],
                                                  mode="transit",
                                                  departure_time=now)

        # Retrieve departure time and return string.
        return "Next bus\n" + directions_result[0]['legs'][0]['departure_time']['text']

app = App()
