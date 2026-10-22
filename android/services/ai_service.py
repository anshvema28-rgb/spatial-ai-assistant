import os
import threading
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in .env file")
        self.client = Groq(api_key=api_key)
        self.conversation_history = []
        self.max_history = 20

    def ask_ai(self, question, callback):
        def _run():
            try:
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
                    *self.conversation_history,
                    {"role": "user", "content": question},
                ]

                response = self.client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=messages,
                    max_tokens=300,
                )

                answer = response.choices[0].message.content
                if not answer:
                    answer = "Sorry bhai, mujhe jawab nahi mila."

                self.conversation_history.extend([
                    {"role": "user", "content": question},
                    {"role": "assistant", "content": answer},
                ])
                self.conversation_history = self.conversation_history[-self.max_history:]

                callback(answer, None)

            except Exception as e:
                callback(None, str(e))

        threading.Thread(target=_run, daemon=True).start()

    def clear_history(self):
        self.conversation_history.clear()