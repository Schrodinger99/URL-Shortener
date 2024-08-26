import sqlite3
import random
import requests
import string
import folium
from datetime import datetime
from geopy.geocoders import Nominatim
import csv

# Database initialization and connection
def init_db():
    conn = sqlite3.connect('url_shortener.db')
    cursor = conn.cursor()

    # Create the URLs table
    cursor.execute('''CREATE TABLE IF NOT EXISTS urls (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        original_url TEXT NOT NULL,
                        short_url TEXT NOT NULL UNIQUE
                      )''')

    # Create the access logs table
    cursor.execute('''CREATE TABLE IF NOT EXISTS access_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        url_id INTEGER NOT NULL,
                        access_time TEXT NOT NULL,
                        city TEXT NOT NULL,
                        FOREIGN KEY(url_id) REFERENCES urls(id)
                      )''')

    conn.commit()
    conn.close()

# Function to insert a URL into the database
def insert_url(original_url, short_url):
    conn = sqlite3.connect('url_shortener.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO urls (original_url, short_url) VALUES (?, ?)', (original_url, short_url))
    conn.commit()
    conn.close()

# Function to retrieve the original URL based on the shortened URL
def get_url(short_url):
    conn = sqlite3.connect('url_shortener.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, original_url FROM urls WHERE short_url = ?', (short_url,))
    url_data = cursor.fetchone()
    conn.close()
    return url_data

# Function to insert access data into the database
def insert_access(url_id, access_time, city):
    conn = sqlite3.connect('url_shortener.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO access_logs (url_id, access_time, city) VALUES (?, ?, ?)', (url_id, access_time, city))
    conn.commit()
    conn.close()

# Function to retrieve access data, optionally filtered by URL ID
def get_access_data(url_id=None):
    conn = sqlite3.connect('url_shortener.db')
    cursor = conn.cursor()
    
    if url_id:
        cursor.execute('SELECT access_time, city FROM access_logs WHERE url_id = ?', (url_id,))
    else:
        cursor.execute('SELECT city, COUNT(*) FROM access_logs GROUP BY city')
    
    data = cursor.fetchall()
    conn.close()
    return data

# Function to shorten a URL
def shorten_url():
    original_url = input("Enter the original URL: ")
    short_url = generate_short_url()
    insert_url(original_url, short_url)
    print(f"Shortened URL: {short_url}")

# Function to handle accessing a shortened URL
def access_url():
    short_url = input("Enter the shortened URL: ")
    url_data = get_url(short_url)
    if url_data:
        url_id, original_url = url_data
        print(f"Redirecting to {original_url}...")

        access_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        city = get_location_from_ip()
        
        insert_access(url_id, access_time, city)
        print(f"Access logged at {access_time} from {city}")
    else:
        print("Short URL not found.")

# Function to get the user's city based on their IP address
def get_location_from_ip():
    try:
        response = requests.get('https://ipinfo.io/json')
        data = response.json()
        city = data.get('city', 'Unknown')
        return city
    except Exception as e:
        print(f"Error fetching location: {e}")
        return "Unknown"

# Function to generate a random short URL
def generate_short_url(length=6):
    characters = string.ascii_letters + string.digits
    short_url = "Styla/" + ''.join(random.choice(characters) for _ in range(length))
    return short_url

# Function to generate a CSV report for a specific shortened URL
def generate_report_for_url(short_url):
    url_data = get_url(short_url)
    if not url_data:
        print("Short URL not found.")
        return
    
    url_id, original_url = url_data
    access_data = get_access_data(url_id)

    if not access_data:
        print("No access data available for this URL.")
        return

    csv_filename = f"report_{short_url.replace('/', '_')}.csv"
    
    with open(csv_filename, 'w', newline='') as csvfile:
        fieldnames = ['Access Time', 'City']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for access_time, city in access_data:
            writer.writerow({'Access Time': access_time, 'City': city})
    
    print(f"Report generated: {csv_filename}")

# Function to generate a heatmap for a specific shortened URL
def generate_heatmap_for_url(short_url):
    url_data = get_url(short_url)
    if not url_data:
        print("Short URL not found.")
        return
    
    url_id, original_url = url_data
    access_data = get_access_data(url_id)

    if not access_data:
        print("No access data available for this URL.")
        return

    m = folium.Map(location=[0, 0], zoom_start=2)

    for access_time, city in access_data:
        geolocator = Nominatim(user_agent="url_shortener")
        location = geolocator.geocode(city)
        if location:
            folium.CircleMarker(
                location=[location.latitude, location.longitude],
                radius=5,
                popup=f"{city}: accessed on {access_time}",
                color='blue',
                fill=True,
                fill_color='blue'
            ).add_to(m)

    heatmap_filename = f"heatmap_{short_url.replace('/', '_')}.html"
    m.save(heatmap_filename)
    print(f"Heatmap generated as {heatmap_filename}")

# Function to generate a heatmap for all data (optional)
def generate_heatmap():
    data = get_access_data()

    if not data:
        print("No access data available.")
        return

    m = folium.Map(location=[0, 0], zoom_start=2)

    for city, count in data:
        geolocator = Nominatim(user_agent="url_shortener")
        location = geolocator.geocode(city)
        if location:
            folium.CircleMarker(
                location=[location.latitude, location.longitude],
                radius=count,
                popup=f"{city}: {count} accesses",
                color='blue',
                fill=True,
                fill_color='blue'
            ).add_to(m)

    m.save('heatmap.html')
    print("Heatmap generated as heatmap.html")

# Main menu to navigate through the options
def main_menu():
    while True:
        print("\n1. Shorten a URL")
        print("2. Access a Shortened URL")
        print("3. Generate Heatmap for All URLs")
        print("4. Generate Report for a URL")
        print("5. Generate Heatmap for a URL")
        print("6. Exit")
        choice = input("Choose an option: ")

        if choice == '1':
            shorten_url()
        elif choice == '2':
            access_url()
        elif choice == '3':
            generate_heatmap()
        elif choice == '4':
            short_url = input("Enter the shortened URL: ")
            generate_report_for_url(short_url)
        elif choice == '5':
            short_url = input("Enter the shortened URL: ")
            generate_heatmap_for_url(short_url)
        elif choice == '6':
            break
        else:
            print("Invalid option. Please try again.")

init_db()  # Initialize the database before starting the application
main_menu()  # Start the main menu
