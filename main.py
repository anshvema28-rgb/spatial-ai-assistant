import os
import datetime
import requests
import speech_recognition as sr
import pyttsx3
from dotenv import load_dotenv
from groq import Groq


# =========================
# API SETUP
# =========================

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError(
        "GROQ_API_KEY nahi mili. Project ki .env file check karo."
    )

client = Groq(api_key=api_key)


# =========================
# VOICE SETUP
# =========================

engine = pyttsx3.init()
engine.setProperty("rate", 160)
engine.setProperty("volume", 1.0)

recognizer = sr.Recognizer()
recognizer.pause_threshold = 0.8


# =========================
# CONVERSATION MEMORY
# =========================

conversation_history = []
MAX_HISTORY_MESSAGES = 20


# =========================
# SPEAK FUNCTION
# =========================

def speak(text):
    global engine

    if not text:
        return

    text = str(text)
    print("Assistant:", text, flush=True)

    try:
        engine.stop()
        engine = pyttsx3.init()
        engine.setProperty("rate", 160)
        engine.setProperty("volume", 1.0)

        engine.say(text)
        engine.runAndWait()

    except Exception as error:
        print("Voice error:", repr(error), flush=True)
# =========================
# AI FUNCTION
# =========================

def ask_ai(question):
    global conversation_history

    messages = [
        {
            "role": "system",
            "content": (
                "You are a friendly voice assistant. "
                "Reply in simple Roman Hinglish using English letters. "
                "Never use Devanagari script. "
                "Keep answers natural and concise, "
                "so they are easy to speak aloud."
            ),
        },
        *conversation_history,
        {"role": "user", "content": question},
    ]

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            max_tokens=300,
        )

        answer = response.choices[0].message.content

        if not answer:
            answer = "Sorry bhai, mujhe jawab nahi mila."

        conversation_history.extend([
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer},
        ])

        conversation_history = conversation_history[
            -MAX_HISTORY_MESSAGES:
        ]

        return answer

    except Exception as error:
        print("AI error:", repr(error), flush=True)
        return (
            "Sorry bhai, AI se connect karne mein problem aa rahi hai."
        )


# =========================
# WEATHER FUNCTION
# =========================

def get_weather(city="Gorakhpur"):
    try:
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"

        geo_response = requests.get(
            geo_url,
            params={
                "name": city,
                "count": 1,
                "language": "en",
            },
            timeout=10,
        )
        geo_response.raise_for_status()

        geo_data = geo_response.json()

        if not geo_data.get("results"):
            return f"Bhai, {city} sheher nahi mila."

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
                "current": (
                    "temperature_2m,"
                    "relative_humidity_2m,"
                    "apparent_temperature,"
                    "weather_code,"
                    "wind_speed_10m"
                ),
                "timezone": "auto",
            },
            timeout=10,
        )
        weather_response.raise_for_status()

        weather_data = weather_response.json()
        weather = weather_data.get("current", {})

        if not weather:
            return "Bhai, abhi weather data nahi mil raha."

        temperature = weather.get("temperature_2m", "unknown")
        feels_like = weather.get("apparent_temperature", "unknown")
        humidity = weather.get("relative_humidity_2m", "unknown")
        wind = weather.get("wind_speed_10m", "unknown")
        code = weather.get("weather_code", -1)

        conditions = {
            0: "saaf aasman",
            1: "zyadatar saaf",
            2: "kuch badal",
            3: "badal chhaye hue",
            45: "kohra",
            48: "kohra",
            51: "halki boondabandi",
            53: "boondabandi",
            55: "tez boondabandi",
            61: "halki baarish",
            63: "baarish",
            65: "tez baarish",
            71: "halki barfbaari",
            73: "barfbaari",
            75: "tez barfbaari",
            80: "baarish ki bauchharein",
            81: "baarish ki bauchharein",
            82: "tez baarish ki bauchharein",
            95: "garaj ke saath baarish",
            96: "ole aur garaj",
            99: "tez garaj aur ole",
        }

        condition = conditions.get(
            code, "mausam ki sthiti saamanya"
        )

        return (
            f"{place_name} ka abhi ka mausam: {condition}. "
            f"Temperature {temperature} degree Celsius hai. "
            f"Feels like {feels_like} degree hai. "
            f"Humidity {humidity} percent aur hawa ki speed "
            f"{wind} kilometer per hour hai."
        )

    except Exception as error:
        print("Weather error:", repr(error), flush=True)
        return (
            "Bhai, weather check nahi ho paaya. "
            "Internet connection check karo."
        )


# =========================
# MICROPHONE LISTEN FUNCTION
# =========================

def listen():
    try:
        with sr.Microphone() as source:
            print("\nListening... Bolo bhai!", flush=True)

            recognizer.adjust_for_ambient_noise(
                source,
                duration=0.4,
            )

            audio = recognizer.listen(
                source,
                timeout=8,
                phrase_time_limit=12,
            )

        question = recognizer.recognize_google(
            audio,
            language="en-IN",
        )

        question = question.strip()

        if question:
            print("You:", question, flush=True)

        return question

    except sr.WaitTimeoutError:
        print("Bhai, awaaz nahi aayi. Dobara bolo.", flush=True)

    except sr.UnknownValueError:
        print("Bhai, baat samajh nahi aayi.", flush=True)

    except sr.RequestError as error:
        print("Speech recognition error:", repr(error), flush=True)

    except Exception as error:
        print("Microphone error:", repr(error), flush=True)

    return ""


# =========================
# QUESTION HANDLER
# =========================

def handle_question(question):
    q = question.lower().strip()

    # Assistant band karne ke commands
    stop_words = [
        "assistant band",
        "band ho jao",
        "band karo",
        "exit",
        "quit",
        "stop assistant",
        "alvida",
    ]

    if any(word in q for word in stop_words):
        return None

    # Date and time
    time_words = [
        "time",
        "samay",
        "kitne baje",
        "waqt",
    ]

    if any(word in q for word in time_words):
        current_time = datetime.datetime.now().strftime(
            "%I:%M %p"
        )
        return f"Bhai, abhi {current_time} baj rahe hain."

    date_words = [
        "date",
        "tareekh",
        "tarikh",
        "aaj ki tarikh",
        "aaj ka din",
    ]

    if any(word in q for word in date_words):
        today = datetime.datetime.now().strftime("%d %B %Y")
        return f"Bhai, aaj {today} hai."

    # Weather
    weather_words = [
        "weather",
        "mausam",
        "temperature",
        "baarish hogi",
    ]

    if any(word in q for word in weather_words):
        known_cities = [
            "gorakhpur",
            "delhi",
            "lucknow",
            "mumbai",
            "kanpur",
            "patna",
            "jaipur",
            "agra",
            "varanasi",
        ]

        city = "Gorakhpur"

        for name in known_cities:
            if name in q:
                city = name.title()
                break

        return get_weather(city)

    # Baaki sawaalon ke liye AI
    return ask_ai(question)


# =========================
# MAIN PROGRAM
# =========================

def main():
    speak("Hello boss! Tumhara AI assistant ready hai.")

    try:
        while True:
            question = listen()

            if not question:
                continue

            answer = handle_question(question)

            if answer is None:
                speak("Theek hai bhai, assistant band kar raha hoon.")
                break

            # Har jawab awaaz mein bolne ki koshish karega
            speak(answer)
            print("Answer speech function completed", flush=True)

    except KeyboardInterrupt:
        speak("Theek hai bhai, assistant band kar raha hoon.")

    finally:
        try:
            engine.stop()
        except Exception:
            pass

        print("\nAssistant band kiya gaya.", flush=True)


if __name__ == "__main__":
    main()