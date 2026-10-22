import kivy.app
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.logger import Logger
from android.ui.main_layout import MainLayout
from android.services.ai_service import AIService
from android.services.system_service import SystemService
from android.services.voice_service import VoiceService
from android.services.permissions import request_required_permissions, request_audio_permission, request_camera_permission
import threading


class SpatialAIApp(kivy.app.App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ai_service = None
        self.system_service = None
        self.voice_service = None
        self.is_listening = False
        self.main_layout = None

    def build(self):
        # Request permissions early
        request_required_permissions(self.on_permissions_result)

        # Initialize services
        try:
            self.ai_service = AIService()
            Logger.info('AI Service initialized')
        except Exception as e:
            Logger.error(f'AI Service init failed: {e}')

        self.system_service = SystemService()
        self.voice_service = VoiceService()

        # Create main layout
        self.main_layout = MainLayout(self)

        # Welcome message
        Clock.schedule_once(lambda dt: self.main_layout.add_conversation(
            'SYSTEM', 'Spatial Holographic Interface initialized. Ready for commands.', 'system'
        ), 0.5)

        return self.main_layout

    def on_permissions_result(self, granted, message):
        Logger.info(f'Permissions: {granted} - {message}')
        if not granted:
            self.main_layout.add_conversation('SYSTEM', 'Some permissions denied. Voice and camera features may not work.', 'system')

    def on_text_send(self, text):
        if not text.strip():
            return
        self.main_layout.add_conversation('USER', text, 'user')
        self.process_question(text)

    def on_mic_toggle(self, instance):
        if self.is_listening:
            self.stop_listening()
        else:
            self.start_listening()

    def start_listening(self):
        if self.is_listening:
            return

        def _on_audio_permission(granted):
            if granted:
                self._do_listen()
            else:
                self.main_layout.add_conversation('SYSTEM', 'Microphone permission required for voice input.', 'system')
                self.main_layout.set_mic_listening(False)

        request_audio_permission(_on_audio_permission)

    def _do_listen(self):
        self.is_listening = True
        self.main_layout.set_mic_listening(True)
        self.main_layout.set_orb_state('listening')

        def stt_callback(text):
            Clock.schedule_once(lambda dt: self.on_speech_recognized(text), 0)

        self.voice_service.listen(stt_callback, language='en-IN')

    def stop_listening(self):
        self.is_listening = False
        self.main_layout.set_mic_listening(False)
        self.main_layout.set_orb_state('idle')
        self.voice_service.stop()

    def on_speech_recognized(self, text):
        self.is_listening = False
        self.main_layout.set_mic_listening(False)
        self.main_layout.set_orb_state('idle')

        if not text or text.startswith('STT error') or text.startswith('Speech recognition'):
            self.main_layout.add_conversation('SYSTEM', f'Recognition failed: {text}', 'system')
            return

        self.main_layout.add_conversation('USER', text, 'user')
        self.process_question(text)

    def process_question(self, question):
        self.main_layout.set_ai_processing(True)
        self.main_layout.set_orb_state('processing')

        def system_callback(response, error):
            Clock.schedule_once(lambda dt: self.on_system_response(response, error), 0)

        self.system_service.handle_question(question, system_callback)

    def on_system_response(self, response, error):
        self.main_layout.set_ai_processing(False)
        self.main_layout.set_orb_state('idle')

        if error:
            self.main_layout.add_conversation('SYSTEM', f'System error: {error}', 'system')
            return

        if response == 'exit':
            self.main_layout.add_conversation('ASSISTANT', 'Theek hai bhai, assistant band kar raha hoon.', 'assistant')
            self.speak_response('Theek hai bhai, assistant band kar raha hoon.')
            Clock.schedule_once(lambda dt: self.stop(), 2)
            return

        if response == 'ai_fallback':
            self.ask_ai(question)
            return

        # Direct system response (time, date, weather, android actions)
        self.main_layout.add_conversation('ASSISTANT', response, 'assistant')
        self.speak_response(response)

    def ask_ai(self, question):
        self.main_layout.set_ai_processing(True)
        self.main_layout.set_orb_state('processing')

        def ai_callback(answer, error):
            Clock.schedule_once(lambda dt: self.on_ai_response(answer, error), 0)

        self.ai_service.ask_ai(question, ai_callback)

    def on_ai_response(self, answer, error):
        self.main_layout.set_ai_processing(False)
        self.main_layout.set_orb_state('idle')

        if error:
            self.main_layout.add_conversation('SYSTEM', f'AI error: {error}', 'system')
            self.speak_response('Sorry bhai, AI se connect karne mein problem aa rahi hai.')
            return

        self.main_layout.add_conversation('ASSISTANT', answer, 'assistant')
        self.speak_response(answer)

    def speak_response(self, text):
        self.main_layout.set_tts_speaking(True)

        def tts_done():
            Clock.schedule_once(lambda dt: self.main_layout.set_tts_speaking(False), 0)

        # Speak in background thread
        def _speak():
            self.voice_service.speak(text)
            tts_done()

        threading.Thread(target=_speak, daemon=True).start()

    def minimize_app(self, instance):
        # On Android, this would minimize the app
        # For desktop testing, just hide window
        from kivy.core.window import Window
        Window.minimize()

    def close_app(self, instance):
        self.stop()

    def on_stop(self):
        if self.voice_service:
            self.voice_service.stop()
        Logger.info('Spatial AI Assistant stopped')


if __name__ == '__main__':
    SpatialAIApp().run()