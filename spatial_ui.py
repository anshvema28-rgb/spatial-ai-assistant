import customtkinter as ctk
import tkinter as tk
from tkinter import scrolledtext
import threading
import time
import math
import os
import random
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class SpatialHolographicUI:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Spatial AI Assistant")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        self.root.overrideredirect(True)
        
        self.is_listening = False
        self.is_processing = False
        self.orb_angle = 0
        self.orb_pulse = 0
        self.particles = []
        self.conversation_history = []
        self.system_info = {
            "cpu": "0%",
            "ram": "0%",
            "mic": "Ready",
            "api": "Connected"
        }
        
        self.setup_window()
        self.create_ui()
        self.start_animations()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def setup_window(self):
        self.root.attributes("-alpha", 0.98)
        self.root.configure(fg_color="#0a0a12")
        
    def create_ui(self):
        self.main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=2, pady=2)
        
        self.create_title_bar()
        self.create_central_orb()
        self.create_side_panels()
        self.create_bottom_input()
        
    def create_title_bar(self):
        title_bar = ctk.CTkFrame(self.main_container, height=40, fg_color="#0d0d1a", corner_radius=0)
        title_bar.pack(fill="x", pady=(0, 2))
        title_bar.pack_propagate(False)
        
        title_label = ctk.CTkLabel(
            title_bar,
            text="SPATIAL HOLOGRAPHIC INTERFACE",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#00ffff"
        )
        title_label.pack(side="left", padx=20, pady=8)
        
        status_frame = ctk.CTkFrame(title_bar, fg_color="transparent")
        status_frame.pack(side="left", padx=15)
        
        self.status_indicator = ctk.CTkLabel(
            status_frame,
            text="●",
            font=ctk.CTkFont(size=12),
            text_color="#00ff88"
        )
        self.status_indicator.pack(side="left")
        
        self.status_text = ctk.CTkLabel(
            status_frame,
            text="SYSTEM ONLINE",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color="#88ffaa"
        )
        self.status_text.pack(side="left", padx=(5, 0))
        
        time_frame = ctk.CTkFrame(title_bar, fg_color="transparent")
        time_frame.pack(side="right", padx=20)
        
        self.time_label = ctk.CTkLabel(
            time_frame,
            text="",
            font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
            text_color="#00ffff"
        )
        self.time_label.pack(side="right", pady=8)
        
        btn_frame = ctk.CTkFrame(title_bar, fg_color="transparent")
        btn_frame.pack(side="right", padx=10)
        
        minimize_btn = ctk.CTkButton(
            btn_frame,
            text="─",
            width=36,
            height=30,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#1a1a2e",
            hover_color="#2a2a4a",
            text_color="#00ffff",
            corner_radius=6,
            command=self.minimize_window
        )
        minimize_btn.pack(side="left", padx=2)
        
        close_btn = ctk.CTkButton(
            btn_frame,
            text="✕",
            width=36,
            height=30,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#2a0a1a",
            hover_color="#4a1a2a",
            text_color="#ff4466",
            corner_radius=6,
            command=self.on_close
        )
        close_btn.pack(side="left", padx=2)
        
    def create_central_orb(self):
        center_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        center_frame.pack(fill="both", expand=True, pady=10)
        
        self.orb_canvas = tk.Canvas(
            center_frame,
            bg="#0a0a12",
            highlightthickness=0,
            width=400,
            height=400
        )
        self.orb_canvas.pack(expand=True)
        
        self.orb_canvas.bind("<Configure>", self.on_canvas_resize)
        
    def create_side_panels(self):
        panels_container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        panels_container.pack(fill="x", padx=20, pady=(0, 10))
        
        left_panel = self.create_glass_panel(panels_container, "AI STATUS", width=350)
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        self.create_status_panel(left_panel)
        
        center_panel = self.create_glass_panel(panels_container, "CONVERSATION LOG", width=450)
        center_panel.pack(side="left", fill="both", expand=True, padx=5)
        self.create_conversation_panel(center_panel)
        
        right_panel = self.create_glass_panel(panels_container, "SYSTEM INFO", width=350)
        right_panel.pack(side="right", fill="y", padx=(10, 0))
        self.create_system_panel(right_panel)
        
    def create_glass_panel(self, parent, title, width=350):
        panel = ctk.CTkFrame(
            parent,
            width=width,
            fg_color=("#151528", "#0d0d1a"),
            corner_radius=16,
            border_width=1,
            border_color="#00ffff40"
        )
        panel.pack_propagate(False)
        
        header = ctk.CTkFrame(panel, fg_color="transparent", height=45)
        header.pack(fill="x", padx=15, pady=(12, 5))
        header.pack_propagate(False)
        
        title_label = ctk.CTkLabel(
            header,
            text=title,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color="#00ffff"
        )
        title_label.pack(side="left")
        
        accent_line = ctk.CTkFrame(header, height=2, fg_color="#00ffff", width=60)
        accent_line.pack(side="left", padx=(10, 0), pady=(0, 8))
        
        content = ctk.CTkFrame(panel, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        
        panel.content_frame = content
        return panel
        
    def create_status_panel(self, panel):
        content = panel.content_frame
        
        self.orb_status_canvas = tk.Canvas(
            content,
            bg="#0d0d1a",
            highlightthickness=0,
            height=120
        )
        self.orb_status_canvas.pack(fill="x", pady=(0, 15))
        
        status_grid = ctk.CTkFrame(content, fg_color="transparent")
        status_grid.pack(fill="x")
        
        self.status_items = {}
        statuses = [
            ("VOICE INPUT", "mic_status", "STANDBY", "#ffaa00"),
            ("AI PROCESSING", "ai_status", "IDLE", "#00ffff"),
            ("TTS ENGINE", "tts_status", "READY", "#00ff88"),
            ("NETWORK", "net_status", "ONLINE", "#88ffaa"),
        ]
        
        for i, (label, key, value, color) in enumerate(statuses):
            row = ctk.CTkFrame(status_grid, fg_color="transparent")
            row.pack(fill="x", pady=6)
            
            lbl = ctk.CTkLabel(
                row,
                text=label,
                font=ctk.CTkFont(family="Segoe UI", size=10),
                text_color="#88aaff"
            )
            lbl.pack(side="left")
            
            val = ctk.CTkLabel(
                row,
                text=value,
                font=ctk.CTkFont(family="Consolas", size=10, weight="bold"),
                text_color=color
            )
            val.pack(side="right")
            self.status_items[key] = val
            
    def create_conversation_panel(self, panel):
        content = panel.content_frame
        
        self.conversation_display = scrolledtext.ScrolledText(
            content,
            bg="#080812",
            fg="#cceeff",
            font=("Consolas", 10),
            wrap=tk.WORD,
            borderwidth=0,
            highlightthickness=0,
            insertbackground="#00ffff",
            selectbackground="#00ffff40"
        )
        self.conversation_display.pack(fill="both", expand=True)
        self.conversation_display.configure(state="disabled")
        
        self.conversation_display.tag_config("user", foreground="#ffaa00")
        self.conversation_display.tag_config("assistant", foreground="#00ffcc")
        self.conversation_display.tag_config("system", foreground="#88aaff")
        self.conversation_display.tag_config("timestamp", foreground="#5588aa", font=("Consolas", 8))
        
    def create_system_panel(self, panel):
        content = panel.content_frame
        
        info_items = [
            ("CPU USAGE", "cpu", "#ff6666"),
            ("MEMORY", "ram", "#ffaa00"),
            ("MICROPHONE", "mic", "#00ff88"),
            ("API STATUS", "api", "#00ffff"),
        ]
        
        self.system_labels = {}
        for label, key, color in info_items:
            row = ctk.CTkFrame(content, fg_color="transparent")
            row.pack(fill="x", pady=10)
            
            lbl = ctk.CTkLabel(
                row,
                text=label,
                font=ctk.CTkFont(family="Segoe UI", size=10),
                text_color="#88aaff"
            )
            lbl.pack(anchor="w")
            
            val = ctk.CTkLabel(
                row,
                text=self.system_info[key],
                font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
                text_color=color
            )
            val.pack(anchor="w", pady=(2, 0))
            self.system_labels[key] = val
            
        divider = ctk.CTkFrame(content, height=1, fg_color="#00ffff30")
        divider.pack(fill="x", pady=15)
        
        mic_frame = ctk.CTkFrame(content, fg_color="transparent")
        mic_frame.pack(fill="x", pady=5)
        
        self.mic_btn = ctk.CTkButton(
            mic_frame,
            text="🎤  START LISTENING",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            height=50,
            fg_color="#0a3a2a",
            hover_color="#1a5a3a",
            text_color="#00ff88",
            corner_radius=12,
            border_width=2,
            border_color="#00ff88",
            command=self.toggle_listening
        )
        self.mic_btn.pack(fill="x")
        
        self.mic_status_label = ctk.CTkLabel(
            mic_frame,
            text="Microphone: Ready",
            font=ctk.CTkFont(family="Segoe UI", size=9),
            text_color="#88ffaa"
        )
        self.mic_status_label.pack(pady=(8, 0))
        
    def create_bottom_input(self):
        input_container = ctk.CTkFrame(self.main_container, fg_color="transparent", height=80)
        input_container.pack(fill="x", padx=20, pady=(0, 15))
        input_container.pack_propagate(False)
        
        input_frame = ctk.CTkFrame(
            input_container,
            fg_color="#0d0d1a",
            corner_radius=14,
            border_width=1,
            border_color="#00ffff40"
        )
        input_frame.pack(fill="both", expand=True, padx=5)
        
        self.text_input = ctk.CTkEntry(
            input_frame,
            placeholder_text="Type your command...",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color="#080812",
            border_color="#00ffff30",
            text_color="#eef",
            placeholder_text_color="#5588aa",
            height=48,
            corner_radius=10
        )
        self.text_input.pack(side="left", fill="x", expand=True, padx=(15, 10), pady=14)
        self.text_input.bind("<Return>", lambda e: self.send_text_input())
        
        self.send_btn = ctk.CTkButton(
            input_frame,
            text="SEND ▸",
            width=100,
            height=48,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#003344",
            hover_color="#005577",
            text_color="#00ffff",
            corner_radius=10,
            border_width=1,
            border_color="#00ffff",
            command=self.send_text_input
        )
        self.send_btn.pack(side="right", padx=(0, 15), pady=14)
        
    def on_canvas_resize(self, event):
        self.canvas_width = event.width
        self.canvas_height = event.height
        self.orb_center_x = self.canvas_width // 2
        self.orb_center_y = self.canvas_height // 2
        
    def start_animations(self):
        self.animate_orb()
        self.animate_particles()
        self.update_time()
        self.update_system_info()
        
    def animate_orb(self):
        self.orb_canvas.delete("all")
        
        cx, cy = self.orb_center_x, self.orb_center_y
        
        self.orb_angle += 0.015
        self.orb_pulse += 0.08
        
        pulse_factor = 1 + 0.15 * math.sin(self.orb_pulse)
        base_radius = min(self.canvas_width, self.canvas_height) * 0.28 * pulse_factor
        
        for i in range(5):
            ring_radius = base_radius + i * 18
            alpha = int(40 - i * 7)
            color = self.hex_color(0, 255, 255, alpha)
            self.orb_canvas.create_oval(
                cx - ring_radius, cy - ring_radius,
                cx + ring_radius, cy + ring_radius,
                outline=color, width=2
            )
        
        core_radius = base_radius * 0.6
        for i in range(3):
            r = core_radius - i * 8
            r_color = int(20 + i * 30)
            g_color = int(180 + i * 40)
            b_color = 255
            color = f"#{r_color:02x}{g_color:02x}{b_color:02x}"
            self.orb_canvas.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                fill=color, outline=""
            )
        
        glow_radius = base_radius * 1.3
        self.orb_canvas.create_oval(
            cx - glow_radius, cy - glow_radius,
            cx + glow_radius, cy + glow_radius,
            outline="#00ffff", width=1, dash=(4, 4)
        )
        
        for i in range(8):
            angle = self.orb_angle + i * (math.pi / 4)
            r1 = base_radius * 1.1
            r2 = base_radius * 1.4
            x1 = cx + r1 * math.cos(angle)
            y1 = cy + r1 * math.sin(angle)
            x2 = cx + r2 * math.cos(angle)
            y2 = cy + r2 * math.sin(angle)
            self.orb_canvas.create_line(x1, y1, x2, y2, fill="#00ffff", width=2)
            
        if self.is_listening:
            listen_radius = base_radius * 1.6
            listen_alpha = int(100 + 100 * math.sin(self.orb_pulse * 3))
            self.orb_canvas.create_oval(
                cx - listen_radius, cy - listen_radius,
                cx + listen_radius, cy + listen_radius,
                outline="#00ff88", width=3
            )
        elif self.is_processing:
            proc_radius = base_radius * 1.5
            self.orb_canvas.create_oval(
                cx - proc_radius, cy - proc_radius,
                cx + proc_radius, cy + proc_radius,
                outline="#ffaa00", width=3
            )
        
        self.root.after(33, self.animate_orb)
        
    def animate_particles(self):
        if len(self.particles) < 30:
            self.particles.append({
                'x': self.orb_center_x + (random.random() - 0.5) * 200,
                'y': self.orb_center_y + (random.random() - 0.5) * 200,
                'vx': (random.random() - 0.5) * 0.5,
                'vy': (random.random() - 0.5) * 0.5,
                'life': 1.0,
                'size': random.random() * 3 + 1,
                'color': random.choice(['#00ffff', '#00ff88', '#8888ff', '#ff00ff'])
            })
            
        self.orb_canvas.delete("particles")
        new_particles = []
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 0.01
            p['vy'] -= 0.005
            
            if p['life'] > 0:
                alpha = int(p['life'] * 255)
                size = p['size'] * p['life']
                self.orb_canvas.create_oval(
                    p['x'] - size, p['y'] - size,
                    p['x'] + size, p['y'] + size,
                    fill=p['color'], outline="", tags="particles"
                )
                new_particles.append(p)
        self.particles = new_particles
        
        self.root.after(50, self.animate_particles)
        
    def hex_color(self, r, g, b, a):
        return f"#{r:02x}{g:02x}{b:02x}"
        
    def update_time(self):
        now = datetime.now().strftime("%H:%M:%S")
        self.time_label.configure(text=now)
        self.root.after(1000, self.update_time)
        
    def update_system_info(self):
        import psutil
        try:
            cpu = psutil.cpu_percent(interval=0.1)
            ram = psutil.virtual_memory().percent
            self.system_labels['cpu'].configure(text=f"{cpu:.1f}%")
            self.system_labels['ram'].configure(text=f"{ram:.1f}%")
        except:
            pass
        self.root.after(3000, self.update_system_info)
        
    def toggle_listening(self):
        self.is_listening = not self.is_listening
        if self.is_listening:
            self.mic_btn.configure(
                text="🎤  LISTENING...",
                fg_color="#3a0a0a",
                hover_color="#5a1a1a",
                text_color="#ff4466",
                border_color="#ff4466"
            )
            self.mic_status_label.configure(text="Microphone: ACTIVE - Speak now", text_color="#ff6666")
            self.status_items['mic_status'].configure(text="ACTIVE", text_color="#ff4466")
            self.status_indicator.configure(text_color="#ff4466")
            self.status_text.configure(text="LISTENING...", text_color="#ffaa00")
            self.start_voice_listening()
        else:
            self.mic_btn.configure(
                text="🎤  START LISTENING",
                fg_color="#0a3a2a",
                hover_color="#1a5a3a",
                text_color="#00ff88",
                border_color="#00ff88"
            )
            self.mic_status_label.configure(text="Microphone: Ready", text_color="#88ffaa")
            self.status_items['mic_status'].configure(text="STANDBY", text_color="#ffaa00")
            self.status_indicator.configure(text_color="#00ff88")
            self.status_text.configure(text="SYSTEM ONLINE", text_color="#88ffaa")
            
    def start_voice_listening(self):
        def listen_thread():
            try:
                import speech_recognition as sr
                recognizer = sr.Recognizer()
                recognizer.pause_threshold = 0.8
                
                with sr.Microphone() as source:
                    self.root.after(0, lambda: self.mic_status_label.configure(text="Adjusting for ambient noise...", text_color="#ffaa00"))
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    
                    if not self.is_listening:
                        return
                        
                    self.root.after(0, lambda: self.mic_status_label.configure(text="Listening... Speak now", text_color="#00ff88"))
                    
                    audio = recognizer.listen(source, timeout=8, phrase_time_limit=12)
                    
                    if not self.is_listening:
                        return
                        
                    self.root.after(0, lambda: self.mic_status_label.configure(text="Processing speech...", text_color="#ffaa00"))
                    
                    question = recognizer.recognize_google(audio, language="en-IN")
                    question = question.strip()
                    
                    if question:
                        self.root.after(0, lambda: self.add_conversation("USER", question, "user"))
                        self.root.after(0, lambda: self.process_question(question))
                        
            except sr.WaitTimeoutError:
                self.root.after(0, lambda: self.mic_status_label.configure(text="Timeout - No speech detected", text_color="#ff6666"))
            except sr.UnknownValueError:
                self.root.after(0, lambda: self.mic_status_label.configure(text="Could not understand audio", text_color="#ff6666"))
            except sr.RequestError as e:
                self.root.after(0, lambda: self.mic_status_label.configure(text=f"Speech service error: {e}", text_color="#ff6666"))
            except Exception as e:
                self.root.after(0, lambda: self.mic_status_label.configure(text=f"Error: {str(e)[:50]}", text_color="#ff6666"))
            finally:
                self.root.after(0, self.reset_listening)
                
        threading.Thread(target=listen_thread, daemon=True).start()
        
    def reset_listening(self):
        self.is_listening = False
        self.mic_btn.configure(
            text="🎤  START LISTENING",
            fg_color="#0a3a2a",
            hover_color="#1a5a3a",
            text_color="#00ff88",
            border_color="#00ff88"
        )
        self.mic_status_label.configure(text="Microphone: Ready", text_color="#88ffaa")
        self.status_items['mic_status'].configure(text="STANDBY", text_color="#ffaa00")
        self.status_indicator.configure(text_color="#00ff88")
        self.status_text.configure(text="SYSTEM ONLINE", text_color="#88ffaa")
        
    def send_text_input(self):
        text = self.text_input.get().strip()
        if text:
            self.text_input.delete(0, "end")
            self.add_conversation("USER", text, "user")
            self.process_question(text)
            
    def process_question(self, question):
        self.is_processing = True
        self.status_items['ai_status'].configure(text="PROCESSING", text_color="#ffaa00")
        self.status_text.configure(text="AI PROCESSING...", text_color="#ffaa00")
        
        def ai_thread():
            try:
                from groq import Groq
                import os
                
                api_key = os.getenv("GROQ_API_KEY")
                if not api_key:
                    answer = "Error: GROQ_API_KEY not found in .env file"
                else:
                    client = Groq(api_key=api_key)
                    
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
                        *[{"role": "user" if i % 2 == 0 else "assistant", "content": msg} 
                          for i, msg in enumerate(self.conversation_history[-18:])],
                        {"role": "user", "content": question},
                    ]
                    
                    response = client.chat.completions.create(
                        model="openai/gpt-oss-120b",
                        messages=messages,
                        max_tokens=300,
                    )
                    
                    answer = response.choices[0].message.content or "Sorry, no response received."
                    
            except Exception as e:
                answer = f"AI Error: {str(e)[:100]}"
                
            self.root.after(0, lambda: self.finish_processing(question, answer))
            
        threading.Thread(target=ai_thread, daemon=True).start()
        
    def finish_processing(self, question, answer):
        self.is_processing = False
        self.add_conversation("ASSISTANT", answer, "assistant")
        self.status_items['ai_status'].configure(text="IDLE", text_color="#00ffff")
        self.status_text.configure(text="SYSTEM ONLINE", text_color="#88ffaa")
        
        self.speak_answer(answer)
        
    def speak_answer(self, text):
        def tts_thread():
            try:
                import pyttsx3
                engine = pyttsx3.init()
                engine.setProperty("rate", 160)
                engine.setProperty("volume", 1.0)
                self.root.after(0, lambda: self.status_items['tts_status'].configure(text="SPEAKING", text_color="#ffaa00"))
                engine.say(text)
                engine.runAndWait()
                self.root.after(0, lambda: self.status_items['tts_status'].configure(text="READY", text_color="#00ff88"))
            except Exception as e:
                self.root.after(0, lambda: self.status_items['tts_status'].configure(text="ERROR", text_color="#ff4466"))
                
        threading.Thread(target=tts_thread, daemon=True).start()
        
    def add_conversation(self, sender, message, tag):
        self.conversation_display.configure(state="normal")
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.conversation_display.insert("end", f"[{timestamp}] ", "timestamp")
        self.conversation_display.insert("end", f"{sender}: ", tag)
        self.conversation_display.insert("end", f"{message}\n\n")
        self.conversation_display.configure(state="disabled")
        self.conversation_display.see("end")
        
        self.conversation_history.append(f"{sender}: {message}")
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
            
    def minimize_window(self):
        self.root.iconify()
        
    def on_close(self):
        self.root.quit()
        self.root.destroy()
        
    def run(self):
        self.add_conversation("SYSTEM", "Spatial Holographic Interface initialized. Ready for commands.", "system")
        self.root.mainloop()

def main():
    app = SpatialHolographicUI()
    app.run()

if __name__ == "__main__":
    main()