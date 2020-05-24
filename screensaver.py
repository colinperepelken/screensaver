# importing
# you need to install the following to run this file:
# requests
# tkinter
# googlemaps
# images
# PYYAML

# importing
import requests
import json
from tkinter import *
import googlemaps
from datetime import datetime
from datetime import timedelta
from PIL import Image, ImageTk
import yaml
import navitia_wrapper
import json


class App():
    def __init__(self):

        # Initialize global config file.
        self.config = yaml.safe_load(open("config.yml"))

        # Initialize Google Maps API.
        # self.gmaps = googlemaps.Client(key=self.config['google_maps_api_key'])
        # use a session for requests
        self.session = requests.Session()
        self.root = Tk()

        self.weatherFrame = Frame(self.root, bg="black")

        # init labels
        self.weatherLabel = Label(self.weatherFrame, text="")
        self.weatherIcon = Label(self.weatherFrame, borderwidth=0)

        # self.busLabel = Label(text="")
        self.timeLabel = Label(text="")
        self.dateLabel = Label(text="")

        # set layouts
        self.weatherFrame.pack(side=TOP, pady=50)
        self.weatherLabel.pack(side=LEFT, fill=NONE)
        self.weatherIcon.pack(side=LEFT, fill=NONE)
        self.timeLabel.pack(expand=True)
        # self.busLabel.pack(pady=15)
        self.dateLabel.pack(expand=True)

        # set window attributees
        self.root.title("Live Screen")
        self.root.geometry("700x300")
        self.root.attributes("-fullscreen", True)
        self.root.configure(background="black")

        # weather config
        self.weatherLabel.configure(fg="white", background="black")
        self.weatherLabel.configure(font=("Courier", 44))

        # bus config
        # self.busLabel.configure(fg="azure", background="black")
        # self.busLabel.configure(font=("Courier", 100))

        # time config
        self.timeLabel.configure(fg="white", background="black")
        self.timeLabel.configure(font=("Courier", 150))

        # date config
        self.dateLabel.configure(fg="white", background="black")
        self.dateLabel.configure(font=("Courier", 60))

        self.update()
        self.time_update()
        # self.bus_update()
        self.date_update()
        self.root.mainloop()

    # update function
    def update(self):
        try:
            self.weatherLabel.configure(text=self.get_weather())
            self.root.after(1000, self.update)
        except Exception as e:
            print("Exception occurred while getting weather: " + str(e))
        #try:
        #    self.busLabel.configure(text=self.get_next_bus())
        # except Exception as e:
        #   self.busLabel.configure(text=self.get_next_bus_departure_time())
        # except Exception as e:
        #   print("Exception occured while getting next bus departure time: " + str(e))
            #self.root.after(5000, self.update)

    def time_update(self):
        self.timeLabel.configure(text=self.get_current_time())
        self.root.after(1000, self.time_update)

    def date_update(self):
        self.dateLabel.configure(text=self.get_current_date())
        self.root.after(60000, self.time_update)

    # def bus_update(self):
    #     self.busLabel.configure(text=self.get_next_bus())
    #     # every 5 minutes = 300000 ms
    #     self.root.after(1000, self.time_update)

    # returns weather
    def get_weather(self):
        api_key = self.config['weather_settings']['openweather_api_key']
        parsa_api = 'cb52bfd59abded6aec05d3a17a7dc0c8'
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
            "Clear": "images/clear_sky.png",
            "Haze": "images/clear_sky.png",
            "Clouds": "images/cloudy.png",
            "Snow": "images/snow.png",
            "Rain": "images/rain.png"
        }

        return icon_map[weather]

    # returns current time
    def get_current_time(self):
        return datetime.now().strftime("%-I:%M %p")

    # returns current time
    def get_current_date(self):
      # return datetime.now().strftime('%B %d, %Y')
      return datetime.now().strftime('%A, %B %d')

    # def eta(self, best_bus, today_hour_min):
    #     eta = best_bus - today_hour_min
    #     return eta

    # def get_next_bus(self):
    #
    #     now = datetime.now()
    #     # returns the current day in full mode ie, Monday not Mon
    #     today_day = now.strftime("%A")
    #     # returns the current hour without leading 0
    #     today_hour = now.strftime("%-I")
    #
    #     # returns current hour and time without leading 0 in 12 hour system, format: 830 for 8:30
    #     today_hour_min = now.strftime("%-I%M")
    #     # returns PM or AM
    #     pm_or_am = now.strftime("%p")
    #
    #     best_bus = self.weekday_bus(int(today_hour), int(today_hour_min), pm_or_am)
    #     best_bus_str = str(best_bus)
    #     best_bus_len = len(best_bus_str)
    #
    #     eta_next_bus = self.eta(int(best_bus), int(today_hour_min))
    #     if eta_next_bus >= 50:
    #         eta_next_bus = eta_next_bus - 40
    #     eta_next_bus_str = str(eta_next_bus)
    #
    #     colours = ["LightYellow", "Yellow", "yellow2", "yellow3", "salmon", "light coral",  # 20-15
    #                "orange", "orange1", "orange2", "orange3", "dark orange",                # 14-10
    #                "sienna1", "sienna2", "DarkOrange1", "DarkOrange2",                      # 9-6
    #                "orange red", "OrangeRed2", "OrangeRed3", "red", "red2",                  # 5-1
    #                "white"]
    #
    #     all_eta = [20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    #
    #     if eta_next_bus > 20:
    #         self.busLabel.configure(fg=colours[21])
    #     else:
    #         cIndex = 0
    #         for x in range(0, len(all_eta)):
    #             if eta_next_bus == all_eta[cIndex]:
    #                 self.busLabel.configure(fg=colours[cIndex])
    #             else:
    #                 cIndex = cIndex + 1
    #
    #     if best_bus_len == 4:
    #         first_two_dig = best_bus_str[:2]
    #         last_two_dig = best_bus_str[2:]
    #         best_bus_nice_format = first_two_dig + ':' + last_two_dig
    #     elif best_bus_len == 3:
    #         first_dig = best_bus_str[:1]
    #         last_two_dig = best_bus_str[1:]
    #         best_bus_nice_format = first_dig + ':' + last_two_dig
    #     else:
    #         best_bus_nice_format = best_bus
    #
    #     return eta_next_bus_str + ' mins till \nbus @ ' + best_bus_nice_format
    #
    # def findClosest(self, list, find):
    #     found = -1
    #     for idx in range(len(list)):
    #         if list[idx] > find:  # < for opposite case.
    #             if found == -1:
    #                 found = idx
    #             else:
    #                 if list[idx] < list[found]:  # > for opposite case.
    #                     found = idx
    #
    #     # <- Note indent level, this is OUTSIDE the for loop.
    #     if found == -1:
    #         return -99999
    #     return list[found]
    #
    # def findSecondClosest(self, list, find):
    #     found = -1
    #     for idx in range(len(list)):
    #         if list[idx] > find:  # < for opposite case.
    #             if found == -1:
    #                 found = idx
    #             else:
    #                 if list[idx] < list[found]:  # > for opposite case.
    #                     found = idx
    #
    #     # <- Note indent level, this is OUTSIDE the for loop.
    #     if found == -1:
    #         return -99999
    #     return list[found + 1]
    #
    # def weekday_bus(self, today_hour, today_hour_min, pm_or_am):
    #     UBCO_am = [608, 638, 653, 707, 722, 737, 752, 807, 822, 837, 907, 937, 1007, 1036, 1106, 1136, 1205, 1235]
    #     UBCO_pm = [105, 135, 149, 204, 219, 239, 254, 309, 324, 339, 354, 409, 424, 439, 509, 525, 542, 558, 613, 625,
    #                643, 713, 744, 814, 914, 944, 1014, 1044, 1114, 1146, 1216]
    #
    #     if pm_or_am == 'AM':
    #         best_time = self.findClosest(UBCO_am, today_hour_min);
    #     elif pm_or_am == 'PM':
    #         best_time = self.findClosest(UBCO_pm, today_hour_min);
    #     else:
    #         best_time = 'error'
    #
    #     best_time_test = self.findSecondClosest(UBCO_am, 600);
    #
    #     return best_time

    # def weekday_bus_second(self, today_hour, today_hour_min, pm_or_am):
    #     UBCO_am = [608, 638, 653, 707, 722, 737, 752, 807, 822, 837, 907, 937, 1007, 1036, 1106, 1136, 1205, 1235]
    #     UBCO_pm = [105, 135, 149, 204, 219, 239, 254, 309, 324, 339, 354, 409, 424, 439, 509, 525, 542, 558, 613, 625,
    #                643, 713, 744, 814, 914, 944, 1014, 1044, 1114, 1146, 1216]
    #
    #     if pm_or_am == 'AM':
    #         best_time = self.findSecondClosest(UBCO_am, today_hour_min);
    #     elif pm_or_am == 'PM':
    #         best_time = self.findSecondClosest(UBCO_pm, today_hour_min);
    #     else:
    #         best_time = 'error'
    #
    #     return best_time

    # Returns the next bus departure time as a string.
    # From the Artium Student Residence to UBCO.
    # Next bus time relies on current time.
    # def get_next_bus_departure_time(self):
    #     # Request directions via public transit.
    #     now = datetime.now()
    #   #OLD WAY OF DOING IT VIA GOOGLE MAPS:
    #     directions_result = self.gmaps.directions(self.config['transit_settings']['home_location'],
    #                                               self.config['transit_settings']['destination_location'],
    #                                               mode="transit",
    #                                               departure_time=now)
    #
    #     # Retrieve departure time and return string.
    #      return "Next bus\n" + directions_result[0]['legs'][0]['departure_time']['text']
    #
    #     # Works with Vancouver's translink: as of Aug 19 2019
    #     new_bus = 'https://gtfs.translink.ca/v2/gtfsalerts?apikey=' + self.config['bus_settings']['translink_api']
    # def next_bus(self):
    #     try:
    #         api_key = "g28dc2772-0abf-463a-a5f8-20c06bc892a7"
    #         nav_bus = 'https://api.navitia.io/v1/coverage/ca-bc/routes/route%3AKLW%3A97-Kelowna_R/vehicle_journeys?from_datetime=20190819T060000&items_per_schedule=100&'
    #         url = "https://api.navitia.io/v1/coverage"
    #
    #         coverage = "ca-bc"
    #         nav = navitia_wrapper.Navitia(url=url, token=api_key).instance(coverage)
    #
    #         response = self.session.get(nav_bus,
    #                                 auth=('785cb1b9-00e1-47b4-8271-213a4b720888', ''))
    #         response_json = json.loads(response.text)
    #
    #         res_json = json.loads(response.content.decode('utf-8'))
    #
    #         print(res_json["vehicle_journeys"][0]["stop_times"][0]["stop_point"]["name"],
    #               res_json["vehicle_journeys"][0]["stop_times"][0]["departure_time"])
    #
    #     except Exception as e:
    #         print("Exception: " + str(e))

app = App()
