import datetime
import requests
import threading
from android.services.android_actions import AndroidActions

class SystemService:
    def __init__(self):
        self.android_actions = AndroidActions()
        self.known_cities = [
            "gorakhpur", "delhi", "lucknow", "mumbai", "kanpur",
            "patna", "jaipur", "agra", "varanasi", "bangalore",
            "hyderabad", "chennai", "kolkata", "pune", "ahmedabad"
        ]

    def get_time(self):
        now = datetime.datetime.now()
        return f"Abhi {now.strftime('%I:%M %p')} baj rahe hain."

    def get_date(self):
        today = datetime.datetime.now()
        return f"Aaj {today.strftime('%d %B %Y')} hai."

    def get_weather(self, city="Gorakhpur", callback=None):
        def _run():
            try:
                geo_url = "https://geocoding-api.open-meteo.com/v1/search"
                geo_response = requests.get(
                    geo_url,
                    params={"name": city, "count": 1, "language": "en"},
                    timeout=10,
                )
                geo_response.raise_for_status()
                geo_data = geo_response.json()

                if not geo_data.get("results"):
                    result = f"Bhai, {city} sheher nahi mila."
                    if callback:
                        callback(result)
                    return

                place = geo_data["results"][0]
                latitude = place["latitude"]
                longitude = place["longitude"]
                place_name = place["name"]

                weather_url = "https://api.open-meteo.com/v1/forecast"
                weather_response = requests.get(
                    weather_url,
                    params={
                        "latitude": latitude,
                        "longitude": longitude,
                        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
                        "timezone": "auto",
                    },
                    timeout=10,
                )
                weather_response.raise_for_status()
                weather_data = weather_response.json()
                weather = weather_data.get("current", {})

                if not weather:
                    result = "Bhai, abhi weather data nahi mil raha."
                    if callback:
                        callback(result)
                    return

                temperature = weather.get("temperature_2m", "unknown")
                feels_like = weather.get("apparent_temperature", "unknown")
                humidity = weather.get("relative_humidity_2m", "unknown")
                wind = weather.get("wind_speed_10m", "unknown")
                code = weather.get("weather_code", -1)

                conditions = {
                    0: "saaf aasman", 1: "zyadatar saaf", 2: "kuch badal", 3: "badal chhaye hue",
                    45: "kohra", 48: "kohra", 51: "halki boondabandi", 53: "boondabandi",
                    55: "tez boondabandi", 61: "halki baarish", 63: "baarish", 65: "tez baarish",
                    71: "halki barfbaari", 73: "barfbaari", 75: "tez barfbaari",
                    80: "baarish ki bauchharein", 81: "baarish ki bauchharein", 82: "tez baarish ki bauchharein",
                    95: "garaj ke saath baarish", 96: "ole aur garaj", 99: "tez garaj aur ole",
                }
                condition = conditions.get(code, "mausam ki sthiti saamanya")

                result = (
                    f"{place_name} ka abhi ka mausam: {condition}. "
                    f"Temperature {temperature} degree Celsius hai. "
                    f"Feels like {feels_like} degree hai. "
                    f"Humidity {humidity} percent aur hawa ki speed {wind} kilometer per hour hai."
                )
                if callback:
                    callback(result)

            except Exception as e:
                if callback:
                    callback(f"Bhai, weather check nahi ho paaya: {str(e)[:50]}")

        threading.Thread(target=_run, daemon=True).start()

    def handle_question(self, question, callback):
        q = question.lower().strip()

        stop_words = ["assistant band", "band ho jao", "band karo", "exit", "quit", "stop assistant", "alvida"]
        if any(word in q for word in stop_words):
            callback("exit", None)
            return

        time_words = ["time", "samay", "kitne baje", "waqt", "what time", "current time"]
        if any(word in q for word in time_words):
            callback(self.get_time(), None)
            return

        date_words = ["date", "tareekh", "tarikh", "aaj ki tarikh", "aaj ka din", "today", "what date"]
        if any(word in q for word in date_words):
            callback(self.get_date(), None)
            return

        weather_words = ["weather", "mausam", "temperature", "baarish hogi", "mausam kaisa"]
        if any(word in q for word in weather_words):
            city = "Gorakhpur"
            for name in self.known_cities:
                if name in q:
                    city = name.title()
                    break
            self.get_weather(city, callback)
            return

        # Android commands
        if any(cmd in q for cmd in ["open settings", "settings kholo", "setting kholo"]):
            result = self.android_actions.open_settings()
            callback(result, None)
            return

        if any(cmd in q for cmd in ["open calculator", "calculator kholo", "calc kholo"]):
            result = self.android_actions.open_calculator()
            callback(result, None)
            return

        if any(cmd in q for cmd in ["open camera", "camera kholo", "camera chalu"]):
            result = self.android_actions.open_camera()
            callback(result, None)
            return

        if any(cmd in q for cmd in ["open wifi", "wifi settings", "wifi kholo", "wi-fi settings"]):
            result = self.android_actions.open_wifi_settings()
            callback(result, None)
            return

        if any(cmd in q for cmd in ["open bluetooth", "bluetooth settings", "bluetooth kholo"]):
            result = self.android_actions.open_bluetooth_settings()
            callback(result, None)
            return

        if any(cmd in q for cmd in ["volume badhao", "volume badha", "volume up", "awaz badhao"]):
            result = self.android_actions.volume_up()
            callback(result, None)
            return

        if any(cmd in q for cmd in ["volume kam karo", "volume kam", "volume down", "awaz kam karo"]):
            result = self.android_actions.volume_down()
            callback(result, None)
            return

        # Default to AI
        callback("ai_fallback", None)