from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.metrics import dp
from android.ui.holographic_ui import (
    HolographicOrb, GlassPanel, StatusRow, ConversationPanel,
    InputPanel, TitleBar
)


class MainLayout(FloatLayout):
    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller

        # Background
        with self.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0.04, 0.04, 0.07, 1, mode='rgba')
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        # Title Bar
        self.title_bar = TitleBar(
            on_minimize=self.controller.minimize_app,
            on_close=self.controller.close_app
        )
        self.title_bar.pos_hint = {'top': 1}
        self.add_widget(self.title_bar)

        # Central Orb
        self.orb = HolographicOrb(
            size=(dp(320), dp(320)),
            pos_hint={'center_x': 0.5, 'center_y': 0.55}
        )
        self.add_widget(self.orb)

        # Left Panel - AI Status
        self.status_panel = GlassPanel('AI STATUS', size_hint=(None, None), size=(dp(300), dp(380)))
        self.status_panel.pos_hint = {'x': 0.02, 'center_y': 0.55}
        self._setup_status_panel()
        self.add_widget(self.status_panel)

        # Center Panel - Conversation
        self.conv_panel = ConversationPanel(size_hint=(None, None), size=(dp(420), dp(500)))
        self.conv_panel.pos_hint = {'center_x': 0.5, 'center_y': 0.55}
        self.add_widget(self.conv_panel)

        # Right Panel - System Info
        self.system_panel = GlassPanel('SYSTEM INFO', size_hint=(None, None), size=(dp(300), dp(380)))
        self.system_panel.pos_hint = {'right': 0.98, 'center_y': 0.55}
        self._setup_system_panel()
        self.add_widget(self.system_panel)

        # Bottom Input
        self.input_panel = InputPanel(
            on_send=self.controller.on_text_send,
            on_mic=self.controller.on_mic_toggle
        )
        self.input_panel.pos_hint = {'center_x': 0.5, 'y': 0.02}
        self.add_widget(self.input_panel)

        # System info update timer
        Clock.schedule_interval(self.update_system_info, 3)

    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def _setup_status_panel(self):
        # Mini orb status
        from kivy.uix.widget import Widget
        orb_placeholder = Widget(size_hint_y=None, height=dp(100))
        self.status_panel.add_item(orb_placeholder)

        self.status_rows = {}
        statuses = [
            ('VOICE INPUT', 'mic_status', 'STANDBY', (1, 0.67, 0, 1)),
            ('AI PROCESSING', 'ai_status', 'IDLE', (0, 1, 1, 1)),
            ('TTS ENGINE', 'tts_status', 'READY', (0, 1, 0.5, 1)),
            ('NETWORK', 'net_status', 'ONLINE', (0.5, 1, 0.67, 1)),
        ]

        for label, key, value, color in statuses:
            row = StatusRow(label, value, color)
            self.status_rows[key] = row
            self.status_panel.add_item(row)

    def _setup_system_panel(self):
        self.system_labels = {}
        items = [
            ('CPU USAGE', 'cpu', (1, 0.4, 0.4, 1)),
            ('MEMORY', 'ram', (1, 0.67, 0, 1)),
            ('MICROPHONE', 'mic', (0, 1, 0.5, 1)),
            ('API STATUS', 'api', (0, 1, 1, 1)),
        ]

        for label, key, color in items:
            row = StatusRow(label, '0%', color)
            self.system_labels[key] = row
            self.system_panel.add_item(row)

        # Divider
        from kivy.uix.widget import Widget
        divider = Widget(size_hint_y=None, height=dp(1))
        with divider.canvas:
            from kivy.graphics import Color, Line
            Color(0, 1, 1, 0.2, mode='rgba')
            divider.line = Line(points=[0, 0, dp(280), 0], width=dp(1))
        self.system_panel.add_item(divider)

    def update_system_info(self, dt):
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=0.05)
            ram = psutil.virtual_memory().percent
            self.system_labels['cpu'].set_value(f'{cpu:.1f}%')
            self.system_labels['ram'].set_value(f'{ram:.1f}%')
        except Exception:
            pass

    def set_orb_state(self, state):
        self.orb.set_state(state)

    def set_mic_listening(self, listening):
        self.input_panel.set_mic_state(listening)
        if listening:
            self.status_rows['mic_status'].set_value('ACTIVE', (1, 0.27, 0.4, 1))
            self.title_bar.set_status('● LISTENING...', (1, 0.67, 0, 1))
        else:
            self.status_rows['mic_status'].set_value('STANDBY', (1, 0.67, 0, 1))
            self.title_bar.set_status('● SYSTEM ONLINE', (0, 1, 0.5, 1))

    def set_ai_processing(self, processing):
        if processing:
            self.status_rows['ai_status'].set_value('PROCESSING', (1, 0.67, 0, 1))
            self.title_bar.set_status('● AI PROCESSING...', (1, 0.67, 0, 1))
        else:
            self.status_rows['ai_status'].set_value('IDLE', (0, 1, 1, 1))
            self.title_bar.set_status('● SYSTEM ONLINE', (0, 1, 0.5, 1))

    def set_tts_speaking(self, speaking):
        if speaking:
            self.status_rows['tts_status'].set_value('SPEAKING', (1, 0.67, 0, 1))
        else:
            self.status_rows['tts_status'].set_value('READY', (0, 1, 0.5, 1))

    def add_conversation(self, sender, text, msg_type):
        self.conv_panel.add_message(sender, text, msg_type)

    def update_system_status(self, key, value, color=None):
        if key in self.system_labels:
            self.system_labels[key].set_value(value, color)