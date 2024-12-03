import os

class Config:
    def __init__(self):
        self.TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '7600282342:AAHN89okONQhClVSNb84W8ZL5mnT3agkbB4')
        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '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')
        self.CHANNEL_ID = "@yarseoneiro"
        self.ADMIN_IDS = [6306428168, 297933075]
        self.PREMIUM_GENERATIONS = 1000
        self.INVITE_BONUS = 20
        self.COURSE_BONUS = 10
        self.MAX_COURSE_BONUS = 70

config = Config()

