from flask import Flask, jsonify, request
import mysql.connector
import requests
from datetime import datetime
import schedule
import threading
import time
from flask_cors import CORS
from typing import Dict, Optional, Tuple

app = Flask(__name__)
CORS(app)

API_KEYS = {
    'weather': '4a3088be5908c9cb1292751a168d88aa',
    'pollution': '5506ef3196fab8f9b5d259bfedf0f3fb'
}

LOCATION = {
    'city': "Chennai,IN",
    'lat': 13.0827,
    'lon': 80.2707
}

MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3307,
    'user': 'root',
    'password': '',
    'database': 'earwax_monitoring'
}

def get_weather_data() -> Optional[Dict]:
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={LOCATION['city']}&appid={API_KEYS['weather']}&units=metric"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None

def get_pollution_data() -> Optional[Dict]:
    try:
        url = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={LOCATION['lat']}&lon={LOCATION['lon']}&appid={API_KEYS['pollution']}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching pollution data: {e}")
        return None

def calculate_earwax_increment(current_percentage: float, 
                             temperature: float,
                             humidity: float,
                             pollen: float,
                             dust: float) -> Tuple[float, bool]:
    """
    Calculate earwax increment and determine if reset is needed.
    Returns a tuple of (new_percentage, needs_reset)
    """
    base_increment = 5.0
    
    temp_factor = 1.0 + (temperature - 25) / 50
    humidity_factor = 1.0 + (humidity - 50) / 100
    pollution_factor = 1.0 + ((pollen + dust) - 50) / 200
    
    increment = base_increment * temp_factor * humidity_factor * pollution_factor
    increment = min(25.0, max(0.0, increment))
    
    new_percentage = current_percentage + increment
    
    # If we would exceed 100%, return 0 and signal for reset
    if new_percentage >= 100:
        return 0.0, True
    
    return new_percentage, False

def fetch_realtime_data() -> Optional[Dict]:
    try:
        weather_data = get_weather_data()
        if not weather_data:
            raise Exception("Failed to fetch weather data")
            
        pollution_data = get_pollution_data()
        if not pollution_data:
            raise Exception("Failed to fetch pollution data")
            
        temperature = weather_data['main']['temp']
        humidity = weather_data['main']['humidity']
        
        components = pollution_data['list'][0]['components']
        pollen = components['pm2_5']
        dust = components['pm10']
        
        previous_earwax = fetch_previous_earwax()
        
        # Get new percentage and reset flag
        earwax_percentage, needs_reset = calculate_earwax_increment(
            previous_earwax,
            temperature,
            humidity,
            pollen,
            dust
        )
        
        data = {
            'age': 25,
            'pollen': pollen,
            'dust': dust,
            'humidity': humidity,
            'temperature': round(temperature, 2),
            'traveling': 'Yes',
            'pollen_season': 'No',
            'earwax_percentage': round(earwax_percentage, 2),
            'date_recorded': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # If we need to reset, store an additional reset record
        if needs_reset:
            reset_data = data.copy()
            reset_data['earwax_percentage'] = 100.0
            store_data_to_mysql(reset_data)
            
        return data
        
    except Exception as e:
        print(f"Error in fetch_realtime_data: {e}")
        return None

def fetch_previous_earwax() -> float:
    try:
        with mysql.connector.connect(**MYSQL_CONFIG) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT earwax_percentage 
                FROM earwax_data 
                ORDER BY date_recorded DESC 
                LIMIT 1
            """)
            result = cursor.fetchone()
            return float(result[0]) if result else 0.0
    except Exception as e:
        print(f"Error fetching previous earwax: {e}")
        return 0.0

def store_data_to_mysql(data: Dict) -> bool:
    if not data:
        print("No data to store")
        return False
    
    try:
        with mysql.connector.connect(**MYSQL_CONFIG) as conn:
            cursor = conn.cursor()
            query = """
            INSERT INTO earwax_data 
            (age, pollen, dust, humidity, temperature, traveling, pollen_season, earwax_percentage, date_recorded)
            VALUES 
            (%(age)s, %(pollen)s, %(dust)s, %(humidity)s, %(temperature)s, %(traveling)s, %(pollen_season)s, %(earwax_percentage)s, %(date_recorded)s)
            """
            cursor.execute(query, data)
            conn.commit()
            print(f"Data stored successfully: {data}")
            return True
    except Exception as e:
        print(f"Error storing data: {e}")
        return False

@app.route('/get_earwax_level', methods=['GET'])
def get_earwax_level():
    try:
        with mysql.connector.connect(**MYSQL_CONFIG) as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT earwax_percentage, date_recorded 
                FROM earwax_data 
                ORDER BY date_recorded DESC 
                LIMIT 1
            """)
            result = cursor.fetchone()
            
            if result:
                return jsonify({
                    "earwax_percentage": float(result['earwax_percentage']),
                    "last_updated": result['date_recorded'].strftime('%Y-%m-%d %H:%M:%S')
                })
            return jsonify({
                "earwax_percentage": 0,
                "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
    except Exception as e:
        print(f"Error in get_earwax_level: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/reset_earwax', methods=['GET'])
def reset_earwax():
    try:
        current_data = fetch_realtime_data()
        if not current_data:
            raise Exception("Failed to fetch current data")
            
        reset_data = {
            **current_data,
            'earwax_percentage': 0.0
        }
        
        if not store_data_to_mysql(reset_data):
            raise Exception("Failed to store reset data")
            
        return jsonify({"message": "Reset successful", "earwax_percentage": 0})
    except Exception as e:
        print(f"Error in reset_earwax: {e}")
        return jsonify({"error": str(e)}), 500

def daily_task():
    print("Running daily task...")
    data = fetch_realtime_data()
    if data:
        store_data_to_mysql(data)
    else:
        print("Failed to fetch data for daily task")

def run_scheduler():
    print("Starting scheduler...")
    schedule.every().day.at("11:27").do(daily_task)
    daily_task()  
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
app.run(host="0.0.0.0", port=5000, debug=True)