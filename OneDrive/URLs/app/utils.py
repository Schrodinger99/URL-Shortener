import string
import random
import csv
import os
import requests
from datetime import datetime

def generate_short_url(length = 6):
    characters = string.ascii_letters + string.digits
    short_url = ''.join(random.choise(characters) for _ in range(length))
    return short_url

def generate_csv_report(links):
    filename = 'report_' + datetime.now().strftime('%Y%m%d_%H%M%s') + '.csv'
    filepath = os.path.join('app/static/reports', filename)
    
    with open(filepath, 'w', newline = '') as csvfile:
        filenames = ['Original URL', 'Short URL', 'Clicks', 'Created At']
        writer = csv.DictWriter(csvfile, fieldnames = filenames)
        
        writer.writeheader()
        for link in links:
            writer.writerow({
                'Original URL' : link.original_url,
                'Short URL' : link.short_url,
                'Clicks' : link.clicks,
                'Created At' : link.created_at.strftime('%Y-%m-%d %H:%M%S')
            }) 
            
    return filepath

def get_geo_info(ip_address):
    try:
        response = requests.get(f'https://ipapi.co/{ip_address}/json/')
        response.raise_for_status()  
        data = response.json()
        return {
            'country': data.get('country_name', 'Unknown'),
            'region': data.get('region', 'Unknown'),
            'city': data.get('city', 'Unknown'),
            'latitude': data.get('latitude', 'Unknown'),
            'longitude': data.get('longitude', 'Unknown'),
            'isp': data.get('org', 'Unknown'),
            'timezone': data.get('timezone', 'Unknown')
        }
    except requests.RequestException as e:
        print(f"Error fetching geo info: {e}")
        return 'Unknown'