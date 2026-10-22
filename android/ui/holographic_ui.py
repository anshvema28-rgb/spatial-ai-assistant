from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Ellipse, Line, PushMatrix, PopMatrix, Rotate, Translate
from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.core.window import Window
from kivy.utils import platform
import math
import random


class HolographicOrb(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.angle = 0
        self.pulse = 0
        self.particles = []
        self.state = "idle"  # idle, listening, processing
        self.size_hint = (None, None)
        self.bind(size=self._update_canvas, pos=self._update_canvas)
        Clock.schedule_interval(self.animate, 1/30)

    def _update_canvas(self, *args):
        self.canvas.clear()
        with self.canvas:
            self.draw_orb()

    def draw_orb(self):
        cx = self.center_x
        cy = self.center_y
        base_radius = min(self.width, self.height) * 0.35

        self.pulse += 0.08
        pulse_factor = 1 + 0.15 * math.sin(self.pulse)
        radius = base_radius * pulse_factor

        # Outer glow rings
        for i in range(5):
            ring_radius = radius + i * dp(18)
            alpha = 0.15 - i * 0.025
            Color(0, 1, 1, alpha, mode='rgba')
            Line(circle=(cx, cy, ring_radius), width=dp(2))

        # Core layers
        for i in range(3):
            r = radius * 0.6 - i * dp(8)
            Color(0.1 + i * 0.15, 0.7 + i * 0.1, 1, 0.9 - i * 0.2, mode='rgba')
            Ellipse(pos=(cx - r, cy - r), size=(r * 2, r * 2))

        # Rotating spokes
        self.angle += 0.015
        Color(0, 1, 1, 0.6, mode='rgba')
        for i in range(8):
            a = self.angle + i * (math.pi / 4)
            r1 = radius * 1.1
            r2 = radius * 1.4
            x1 = cx + r1 * math.cos(a)
            y1 = cy + r1 * math.sin(a)
            x2 = cx + r2 * math.cos(a)
            y2 = cy + r2 * math.sin(a)
            Line(points=[x1, y1, x2, y2], width=dp(2))

        # State indicator ring
        if self.state == "listening":
            Color(0, 1, 0.5, 0.8, mode='rgba')
            Line(circle=(cx, cy, radius * 1.6), width=dp(3))
        elif self.state == "processing":
            Color(1, 0.67, 0, 0.8, mode='rgba')
            Line(circle=(cx, cy, radius * 1.5), width=dp(3))

        # Particles
        for p in self.particles:
            Color(*p['color'], p['life'], mode='rgba')
            s = p['size'] * p['life']
            Ellipse(pos=(p['x'] - s, p['y'] - s), size=(s * 2, s * 2))

    def animate(self, dt):
        # Spawn particles
        if len(self.particles) < 25:
            self.particles.append({
                'x': self.center_x + (random.random() - 0.5) * self.width * 0.6,
                'y': self.center_y + (random.random() - 0.5) * self.height * 0.6,
                'vx': (random.random() - 0.5) * 0.8,
                'vy': (random.random() - 0.5) * 0.8 - 0.3,
                'life': 1.0,
                'size': random.random() * dp(4) + dp(2),
                'color': random.choice([
                    (0, 1, 1), (0, 1, 0.5), (0.5, 0.5, 1), (1, 0, 1)
                ])
            })

        # Update particles
        new_particles = []
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] -= 0.01
            p['life'] -= 0.015
            if p['life'] > 0:
                new_particles.append(p)
        self.particles = new_particles

        self._update_canvas()

    def set_state(self, state):
        self.state = state


class GlassPanel(BoxLayout):
    def __init__(self, title, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(12)
        self.spacing = dp(8)
        self.size_hint = (None, 1)
        self.width = dp(320)

        with self.canvas.before:
            Color(0.08, 0.08, 0.16, 0.85, mode='rgba')
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(16)])
            Color(0, 1, 1, 0.25, mode='rgba')
            self.border = Line(rounded_rectangle=(self.pos[0], self.pos[1], self.size[0], self.size[1], dp(16)), width=dp(1.5))

        self.bind(pos=self._update_graphics, size=self._update_graphics)

        # Header
        header = BoxLayout(size_hint_y=None, height=dp(40), orientation='horizontal')
        title_label = Label(
            text=title,
            font_size=sp(13),
            bold=True,
            color=(0, 1, 1, 1),
            halign='left',
            valign='middle',
            size_hint_x=0.7
        )
        title_label.bind(size=title_label.setter('text_size'))
        header.add_widget(title_label)

        accent = BoxLayout(size_hint_x=0.3)
        with accent.canvas:
            Color(0, 1, 1, 1, mode='rgba')
            self.accent_line = Rectangle(pos=(title_label.x + dp(10), title_label.y + dp(4)), size=(dp(60), dp(2)))
        header.add_widget(accent)
        self.add_widget(header)

        self.content = BoxLayout(orientation='vertical', spacing=dp(6))
        self.add_widget(self.content)

    def _update_graphics(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border.rounded_rectangle = (self.pos[0], self.pos[1], self.size[0], self.size[1], dp(16))
        self.accent_line.pos = (self.pos[0] + dp(100), self.pos[1] + self.size[1] - dp(36))

    def add_item(self, widget):
        self.content.add_widget(widget)


class StatusRow(BoxLayout):
    def __init__(self, label, value, value_color=(0, 1, 1, 1), **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(28)
        self.orientation = 'horizontal'

        lbl = Label(
            text=label,
            font_size=sp(10),
            color=(0.5, 0.67, 1, 1),
            halign='left',
            valign='middle',
            size_hint_x=0.6
        )
        lbl.bind(size=lbl.setter('text_size'))

        self.value_label = Label(
            text=value,
            font_size=sp(10),
            bold=True,
            color=value_color,
            halign='right',
            valign='middle',
            size_hint_x=0.4
        )
        self.value_label.bind(size=self.value_label.setter('text_size'))

        self.add_widget(lbl)
        self.add_widget(self.value_label)

    def set_value(self, value, color=None):
        self.value_label.text = value
        if color:
            self.value_label.color = color


class ConversationPanel(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(12)
        self.spacing = dp(8)

        with self.canvas.before:
            Color(0.08, 0.08, 0.16, 0.85, mode='rgba')
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(16)])
            Color(0, 1, 1, 0.25, mode='rgba')
            self.border = Line(rounded_rectangle=(self.pos[0], self.pos[1], self.size[0], self.size[1], dp(16)), width=dp(1.5))

        self.bind(pos=self._update_graphics, size=self._update_graphics)

        header = BoxLayout(size_hint_y=None, height=dp(40), orientation='horizontal')
        title = Label(
            text='CONVERSATION LOG',
            font_size=sp(13),
            bold=True,
            color=(0, 1, 1, 1),
            halign='left',
            valign='middle'
        )
        title.bind(size=title.setter('text_size'))
        header.add_widget(title)
        self.add_widget(header)

        self.scroll = ScrollView()
        self.messages_layout = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None)
        self.messages_layout.bind(minimum_height=self.messages_layout.setter('height'))
        self.scroll.add_widget(self.messages_layout)
        self.add_widget(self.scroll)

    def _update_graphics(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border.rounded_rectangle = (self.pos[0], self.pos[1], self.size[0], self.size[1], dp(16))

    def add_message(self, sender, text, msg_type='assistant'):
        colors = {
            'user': (1, 0.67, 0, 1),
            'assistant': (0, 1, 0.8, 1),
            'system': (0.5, 0.67, 1, 1),
        }
        color = colors.get(msg_type, (1, 1, 1, 1))

        msg_box = BoxLayout(orientation='vertical', size_hint_y=None, padding=dp(8), spacing=dp(2))
        msg_box.bind(minimum_height=msg_box.setter('height'))

        from kivy.uix.label import Label
        time_str = __import__('datetime').datetime.now().strftime('%H:%M:%S')
        time_lbl = Label(
            text=f'[{time_str}] {sender}:',
            font_size=sp(9),
            color=(0.3, 0.5, 0.7, 1),
            halign='left',
            valign='top',
            size_hint_y=None
        )
        time_lbl.bind(texture_size=lambda *x: setattr(time_lbl, 'height', time_lbl.texture_size[1]))
        time_lbl.bind(size=time_lbl.setter('text_size'))

        text_lbl = Label(
            text=text,
            font_size=sp(10),
            color=color,
            halign='left',
            valign='top',
            size_hint_y=None
        )
        text_lbl.bind(texture_size=lambda *x: setattr(text_lbl, 'height', text_lbl.texture_size[1]))
        text_lbl.bind(size=text_lbl.setter('text_size'))

        msg_box.add_widget(time_lbl)
        msg_box.add_widget(text_lbl)
        self.messages_layout.add_widget(msg_box)
        Clock.schedule_once(lambda dt: self.scroll.scroll_to(msg_box), 0.1)


class InputPanel(BoxLayout):
    def __init__(self, on_send, on_mic, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(70)
        self.padding = dp(10)
        self.spacing = dp(10)

        with self.canvas.before:
            Color(0.08, 0.08, 0.16, 0.9, mode='rgba')
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(14)])
            Color(0, 1, 1, 0.25, mode='rgba')
            self.border = Line(rounded_rectangle=(self.pos[0], self.pos[1], self.size[0], self.size[1], dp(14)), width=dp(1.5))

        self.bind(pos=self._update_graphics, size=self._update_graphics)

        self.text_input = TextInput(
            hint_text='Type command...',
            font_size=sp(13),
            background_color=(0.03, 0.03, 0.07, 1),
            foreground_color=(0.93, 0.93, 1, 1),
            hint_text_color=(0.3, 0.5, 0.7, 1),
            cursor_color=(0, 1, 1, 1),
            multiline=False,
            size_hint_x=0.7,
            padding=[dp(12), dp(10)]
        )
        self.text_input.bind(on_text_validate=lambda x: on_send(self.text_input.text))
        self.add_widget(self.text_input)

        self.send_btn = Button(
            text='SEND',
            font_size=sp(12),
            bold=True,
            background_normal='',
            background_color=(0, 0.2, 0.27, 1),
            color=(0, 1, 1, 1),
            size_hint_x=0.15
        )
        self.send_btn.bind(on_press=lambda x: on_send(self.text_input.text))
        with self.send_btn.canvas.before:
            Color(0, 1, 1, 0.5, mode='rgba')
            self.send_border = Line(rounded_rectangle=(self.send_btn.pos[0], self.send_btn.pos[1], self.send_btn.size[0], self.send_btn.size[1], dp(10)), width=dp(1))
        self.send_btn.bind(pos=self._update_send_border, size=self._update_send_border)
        self.add_widget(self.send_btn)

        self.mic_btn = Button(
            text='MIC',
            font_size=sp(12),
            bold=True,
            background_normal='',
            background_color=(0.04, 0.23, 0.16, 1),
            color=(0, 1, 0.5, 1),
            size_hint_x=0.15
        )
        self.mic_btn.bind(on_press=on_mic)
        with self.mic_btn.canvas.before:
            Color(0, 1, 0.5, 0.5, mode='rgba')
            self.mic_border = Line(rounded_rectangle=(self.mic_btn.pos[0], self.mic_btn.pos[1], self.mic_btn.size[0], self.mic_btn.size[1], dp(10)), width=dp(1.5))
        self.mic_btn.bind(pos=self._update_mic_border, size=self._update_mic_border)
        self.add_widget(self.mic_btn)

        self.mic_status = Label(
            text='Microphone: Ready',
            font_size=sp(10),
            color=(0.5, 1, 0.67, 1),
            size_hint_x=0.3
        )
        self.add_widget(self.mic_status)

    def _update_graphics(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border.rounded_rectangle = (self.pos[0], self.pos[1], self.size[0], self.size[1], dp(14))

    def _update_send_border(self, *args):
        self.send_border.rounded_rectangle = (self.send_btn.pos[0], self.send_btn.pos[1], self.send_btn.size[0], self.send_btn.size[1], dp(10))

    def _update_mic_border(self, *args):
        self.mic_border.rounded_rectangle = (self.mic_btn.pos[0], self.mic_btn.pos[1], self.mic_btn.size[0], self.mic_btn.size[1], dp(10))

    def set_mic_state(self, listening):
        if listening:
            self.mic_btn.text = 'LISTENING'
            self.mic_btn.background_color = (0.23, 0.04, 0.04, 1)
            self.mic_btn.color = (1, 0.27, 0.4, 1)
            self.mic_status.text = 'Microphone: ACTIVE - Speak now'
            self.mic_status.color = (1, 0.4, 0.4, 1)
        else:
            self.mic_btn.text = 'MIC'
            self.mic_btn.background_color = (0.04, 0.23, 0.16, 1)
            self.mic_btn.color = (0, 1, 0.5, 1)
            self.mic_status.text = 'Microphone: Ready'
            self.mic_status.color = (0.5, 1, 0.67, 1)


class TitleBar(BoxLayout):
    def __init__(self, on_minimize, on_close, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(44)
        self.padding = [dp(16), dp(4), dp(16), dp(4)]

        with self.canvas.before:
            Color(0.05, 0.05, 0.1, 1, mode='rgba')
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self._update_bg, size=self._update_bg)

        title = Label(
            text='SPATIAL HOLOGRAPHIC INTERFACE',
            font_size=sp(11),
            bold=True,
            color=(0, 1, 1, 1),
            halign='left',
            valign='middle',
            size_hint_x=0.5
        )
        title.bind(size=title.setter('text_size'))
        self.add_widget(title)

        self.status_indicator = Label(
            text='● SYSTEM ONLINE',
            font_size=sp(10),
            color=(0, 1, 0.5, 1),
            halign='left',
            valign='middle',
            size_hint_x=0.3
        )
        self.status_indicator.bind(size=self.status_indicator.setter('text_size'))
        self.add_widget(self.status_indicator)

        self.time_label = Label(
            text='',
            font_size=sp(11),
            bold=True,
            color=(0, 1, 1, 1),
            font_name='RobotoMono' if platform != 'android' else 'DroidSansMono',
            halign='right',
            valign='middle',
            size_hint_x=0.2
        )
        self.time_label.bind(size=self.time_label.setter('text_size'))
        self.add_widget(self.time_label)
        Clock.schedule_interval(self.update_time, 1)

        btn_container = BoxLayout(size_hint_x=None, width=dp(80), spacing=dp(4))
        min_btn = Button(
            text='─',
            font_size=sp(16),
            bold=True,
            background_normal='',
            background_color=(0.1, 0.1, 0.18, 1),
            color=(0, 1, 1, 1),
            size_hint=(None, None),
            size=(dp(36), dp(36))
        )
        min_btn.bind(on_press=on_minimize)
        btn_container.add_widget(min_btn)

        close_btn = Button(
            text='✕',
            font_size=sp(13),
            bold=True,
            background_normal='',
            background_color=(0.16, 0.04, 0.1, 1),
            color=(1, 0.27, 0.4, 1),
            size_hint=(None, None),
            size=(dp(36), dp(36))
        )
        close_btn.bind(on_press=on_close)
        btn_container.add_widget(close_btn)
        self.add_widget(btn_container)

    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def update_time(self, dt):
        self.time_label.text = __import__('datetime').datetime.now().strftime('%H:%M:%S')

    def set_status(self, text, color=(0, 1, 0.5, 1)):
        self.status_indicator.text = text
        self.status_indicator.color = color


# Need to import RoundedRectangle
from kivy.graphics import RoundedRectangle