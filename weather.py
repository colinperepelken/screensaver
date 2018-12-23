import requests
import json
from tkinter import *



class App():
    def __init__(self):
        self.root = Tk()
        self.label = Label(text="")
        self.label.pack()
        self.root.title("Weather")
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

      res_json = json.loads(response.content)

      weather = "Weather: " + res_json["weather"][0]["main"] + "\n"
      low_temp = "Low: " + str(res_json["main"]["temp_min"] - 273.15)  + "\n"
      high_temp = "High: " + str(res_json["main"]["temp_max"] - 273.15)
      text = weather + low_temp + high_temp
      self.label.configure(text=text)
      

app=App()