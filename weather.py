import requests
import matplotlib.pyplot as plt
from tkinter import *
from tkinter import messagebox
from tkinter.font import Font
from PIL import Image, ImageTk
import io

# Function to fetch weather data
def get_weather(city):
    api_key = "eef0a1c4550f45f2a5f64946240908"  # Replace with your actual API key from WeatherAPI
    base_url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={city}&days=1&aqi=no&alerts=no"
    response = requests.get(base_url)
    return response.json()

# Function to display the weather details
def display_weather(weather):
    if 'error' in weather:
        messagebox.showerror("Error", "City not found!")
        return

    city_name = weather['location']['name']
    temperature = weather['current']['temp_c']
    condition = weather['current']['condition']['text']
    humidity = weather['current']['humidity']
    wind_speed = weather['current']['wind_kph']

    current_temp_label.config(text=f"{temperature}°C")
    condition_label.config(text=condition)
    city_label.config(text=city_name)
    humidity_label.config(text=f"Humidity: {humidity}%")
    wind_label.config(text=f"Wind Speed: {wind_speed} kph")

    # Display hourly forecast and create graph
    hourly_forecast = weather['forecast']['forecastday'][0]['hour']
    hourly_text = ""
    hours = []
    temps = []
    rain_time = ""

    for hour in hourly_forecast[::3]:  # Every 3 hours
        hour_time = hour['time'].split(' ')[1][:5]
        temp = hour['temp_c']
        hourly_text += f"{hour_time} {temp}°C\n"
        hours.append(hour_time)
        temps.append(temp)

        if hour.get('will_it_rain', 0) == 1:
            rain_time = hour_time

    if rain_time:
        rain_label.config(text=f"Expected Rain Time: {rain_time}")
    else:
        rain_label.config(text="No Rain Expected")

    hourly_label.config(text=hourly_text)

    # Create a graph for the temperature data
    plt.figure(figsize=(5, 2))
    plt.plot(hours, temps, marker='o')
    plt.title('Temperature over time')
    plt.xlabel('Time')
    plt.ylabel('Temperature (°C)')
    plt.grid(True)

    # Save the graph to a PNG file and display it
    graph_image = io.BytesIO()
    plt.savefig(graph_image, format='png')
    graph_image.seek(0)
    graph_photo = ImageTk.PhotoImage(Image.open(graph_image))
    graph_label.config(image=graph_photo)
    graph_label.image = graph_photo

    switch_to_weather_screen()

# Function to search for weather
def search_weather():
    city = city_text.get().strip()
    if city:
        weather = get_weather(city)
        display_weather(weather)
    else:
        messagebox.showwarning("Input Error", "Please enter a city name.")

# Function to refresh the weather data
def refresh_weather():
    city = city_label.cget("text")
    if city:
        weather = get_weather(city)
        display_weather(weather)

# Function to switch to weather screen
def switch_to_weather_screen():
    entry_screen.pack_forget()
    weather_screen.pack(fill='both', expand=True)

# Function to go back to entry screen
def go_back():
    weather_screen.pack_forget()
    entry_screen.pack(fill='both', expand=True)

# Function to add city to watchlist
def add_to_watchlist():
    city = city_text.get().strip()
    if city and city not in watchlist:
        watchlist.append(city)
        update_watchlist()

# Function to update watchlist display
def update_watchlist():
    for widget in watchlist_frame.winfo_children():
        widget.destroy()

    for city in watchlist:
        city_frame = Frame(watchlist_frame, bg=bg_color)
        city_label = Label(city_frame, text=city, font=small_font, bg=bg_color, fg="black")
        city_label.pack(side=LEFT, padx=10)

        delete_button = Button(city_frame, text="Delete", command=lambda c=city: delete_from_watchlist(c), bg="red",
                               font=('Helvetica', 12), fg="white")
        delete_button.pack(side=RIGHT)

        city_label.bind("<Button-1>", lambda e, c=city: search_weather_watchlist(c))
        city_frame.pack(fill='x', pady=2)

def delete_from_watchlist(city):
    if city in watchlist:
        watchlist.remove(city)
        update_watchlist()

def search_weather_watchlist(city):
    weather = get_weather(city)
    display_weather(weather)

# Initialize the main window
app = Tk()
app.title("WeatherCast")
app.geometry("375x667")  # iPhone 8 dimensions

# Light blue gradient background color
bg_color = "#87CEEB"
bg_color2 = "#4682B4"

# Custom Fonts
large_font = Font(family="Helvetica", size=48, weight="bold")
medium_font = Font(family="Helvetica", size=24)
small_font = Font(family="Helvetica", size=16)

# Watchlist to store favorite cities
watchlist = []

# Entry screen (First screen)
entry_screen = Frame(app, bg=bg_color)
entry_screen.pack(fill='both', expand=True)

# Add the "WeatherCast" heading in the top left corner
heading_label = Label(entry_screen, text="WeatherCast", font=('Helvetica', 24, 'italic'), bg=bg_color, anchor='nw')
heading_label.place(x=10, y=10)

# Add a PNG image to the center
img = Image.open("weather.png")  # Replace with the path to your image file
img = img.resize((150, 150), Image.LANCZOS)
img_photo = ImageTk.PhotoImage(img)
image_label = Label(entry_screen, image=img_photo, bg=bg_color)
image_label.pack(pady=50)

# Entry field for city name
city_text = StringVar()
city_entry = Entry(entry_screen, textvariable=city_text, font=('Helvetica', 18), width=20)
city_entry.pack(pady=10)

# Search button
search_button = Button(entry_screen, text="Search", command=search_weather, bg="white", font=('Helvetica', 16))
search_button.pack(pady=10)

# Watchlist button
watchlist_button = Button(entry_screen, text="Add to Watchlist", command=add_to_watchlist, bg="white",
                          font=('Helvetica', 16))
watchlist_button.pack(pady=10)

# Watchlist display
watchlist_frame = Frame(entry_screen, bg=bg_color)
watchlist_frame.pack(pady=20)

# Weather screen (Second screen)
weather_screen = Frame(app, bg=bg_color2)

# Back button to return to entry screen
back_button = Button(weather_screen, text="Back", command=go_back, bg="white", font=('Helvetica', 16))
back_button.pack(anchor='nw', padx=10, pady=10)

# City name label
city_label = Label(weather_screen, text="", font=medium_font, bg=bg_color2, fg="white")
city_label.pack(pady=10)

# Current temperature label
current_temp_label = Label(weather_screen, text="", font=large_font, bg=bg_color2, fg="white")
current_temp_label.pack(pady=10)

# Weather condition label
condition_label = Label(weather_screen, text="", font=medium_font, bg=bg_color2, fg="white")
condition_label.pack(pady=5)

# Hourly forecast label
hourly_label = Label(weather_screen, text="", font=small_font, bg=bg_color2, fg="white", justify=LEFT)
hourly_label.pack(pady=20)

# Graph label to display the temperature graph
graph_label = Label(weather_screen, bg=bg_color2)
graph_label.pack(pady=10)

# Humidity and Wind Speed labels
humidity_label = Label(weather_screen, text="", font=small_font, bg=bg_color2, fg="white")
humidity_label.pack(pady=5)

wind_label = Label(weather_screen, text="", font=small_font, bg=bg_color2, fg="white")
wind_label.pack(pady=5)

# Rain time label
rain_label = Label(weather_screen, text="", font=small_font, bg=bg_color2, fg="white")
rain_label.pack(pady=5)

# Refresh button to refresh weather data
refresh_button = Button(weather_screen, text="Refresh", command=refresh_weather, bg="white", font=('Helvetica', 16))
refresh_button.pack(pady=10)

# Start with the entry screen
entry_screen.pack(fill='both', expand=True)

# Start the application
app.mainloop()
