import requests
import json
from tkinter import *

api_key = "f5988e28703d9fdcb99201c66e8eabcf"
city = "Kelowna"
response = requests.get("http://api.openweathermap.org/data/2.5/weather?q=" + city + "&appid=" + api_key)

res_json = json.loads(response.content)

weather = "Weather: " + res_json["weather"][0]["main"] + "\n"
low_temp = "Low: " + str(res_json["main"]["temp_min"])  + "\n"
high_temp = "High: " + str(res_json["main"]["temp_max"])

window = Tk()

window.title("Weather")
text = Text(window, height=10, width=30)
text.pack()
text.insert(END, weather)
text.insert(END, low_temp)
text.insert(END, high_temp)

window.mainloop()