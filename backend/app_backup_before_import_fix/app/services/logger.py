from datetime import datetime


class Logger:

    @staticmethod
    def log(agent, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [{agent}] {message}")
