import sys

print("Testing pyttsx3 TTS engine...")
try:
    import pyttsx3
    engine = pyttsx3.init()
    test_sentence = "Hello bhai, mera voice test chal raha hai."
    engine.say(test_sentence)
    engine.runAndWait()
    print("pyttsx3 test completed successfully.")
except Exception as e:
    print(f"pyttsx3 error: {e}")
    sys.exit(1)

print("\nMicrophone Permission Check")
print("The microphone will be used for a short 5 second test to verify SpeechRecognition and PyAudio.")
user_input = input("Do you agree to allow microphone access for this test? (yes/no): ").strip().lower()
if user_input not in ("yes", "y"):
    print("Microphone test skipped by user.")
    sys.exit(0)

try:
    import speech_recognition as sr
except Exception as e:
    print(f"SpeechRecognition import error: {e}")
    sys.exit(1)

recognizer = sr.Recognizer()
try:
    mic = sr.Microphone()
except Exception as e:
    print(f"Microphone device unavailable: {e}")
    sys.exit(1)

print("Listening for up to 5 seconds. Speak now...")
try:
    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
except sr.WaitTimeoutError:
    print("No speech detected within timeout.")
    sys.exit(0)
except Exception as e:
    print(f"Microphone error: {e}")
    sys.exit(1)

print("Recognizing speech with English engine...")
try:
    text = recognizer.recognize_google(audio, language="en-IN")
    print(f"Recognized text: {text}")
except sr.UnknownValueError:
    print("Speech was unintelligible.")
except sr.RequestError as e:
    print(f"Recognition service error: {e}")
except Exception as e:
    print(f"Recognition error: {e}")

print("\nNote: This test uses English language settings. Hinglish recognition will be configured later.")
