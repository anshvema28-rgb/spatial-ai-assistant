from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger

from android.ui.main_layout import MainLayout


class SpatialAIAssistantApp(App):
    title = "Spatial AI Assistant"

    def build(self):
        Logger.info("SpatialAI: Starting app")

        try:
            self.root_layout = MainLayout()
            return self.root_layout
        except Exception:
            Logger.exception("SpatialAI: Failed to create MainLayout")
            raise

    def on_start(self):
        Logger.info("SpatialAI: App started")
        Clock.schedule_once(self._initialize_services, 0)

    def _initialize_services(self, dt):
        """Initialize optional services only if their APIs are known."""
        Logger.info("SpatialAI: Main screen initialized")

    def on_pause(self):
        # Allow Android to pause the app without exiting.
        return True

    def on_resume(self):
        Logger.info("SpatialAI: App resumed")

    def on_stop(self):
        Logger.info("SpatialAI: App stopped")


if __name__ == "__main__":
    SpatialAIAssistantApp().run()