try:
    from plyer import tts, stt
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False

try:
    from jnius import autoclass
    ANDROID_TTS_AVAILABLE = True
except ImportError:
    ANDROID_TTS_AVAILABLE = False

class VoiceService:
    def __init__(self):
        self.plyer_available = PLYER_AVAILABLE
        self.android_tts_available = ANDROID_TTS_AVAILABLE
        self.tts_engine = None
        self._init_android_tts()

    def _init_android_tts(self):
        if self.android_tts_available:
            try:
                self.TextToSpeech = autoclass('android.speech.tts.TextToSpeech')
                self.PythonActivity = autoclass('org.kivy.android.PythonActivity')
                self.Locale = autoclass('java.util.Locale')
                activity = self.PythonActivity.mActivity
                self.tts_engine = self.TextToSpeech(activity, None)
            except Exception:
                self.tts_engine = None

    def speak(self, text, language="en-IN"):
        if not text:
            return

        if self.tts_engine:
            try:
                self.tts_engine.setLanguage(self.Locale("en", "IN"))
                self.tts_engine.speak(text, self.TextToSpeech.QUEUE_FLUSH, None, "utterance_1")
                return
            except Exception:
                pass

        if self.plyer_available:
            try:
                tts.speak(text)
                return
            except Exception:
                pass

        print(f"[TTS Fallback] {text}")

    def listen(self, callback, language="en-IN"):
        if self.plyer_available:
            try:
                stt.listen(callback=callback, language=language)
                return
            except Exception as e:
                callback(f"STT error: {str(e)[:50]}")
                return

        callback("Speech recognition not available on this platform")

    def stop(self):
        if self.tts_engine:
            try:
                self.tts_engine.stop()
            except Exception:
                pass

    def is_available(self):
        return self.plyer_available or self.android_tts_available