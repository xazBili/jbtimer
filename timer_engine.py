import time


class TimerEngine:
    def __init__(self):
        self.elapsed = 0.0
        self.running = False
        self.last_tick = None

    def start(self):
        if not self.running:
            self.running = True
            self.last_tick = time.monotonic()

    def pause(self):
        if self.running:
            self._sync()
            self.running = False

    def toggle(self):
        if self.running:
            self.pause()
        else:
            self.start()

    def reset(self):
        self.running = False
        self.elapsed = 0.0
        self.last_tick = None

    def _sync(self):
        if self.running and self.last_tick is not None:
            now = time.monotonic()
            self.elapsed += now - self.last_tick
            self.last_tick = now

    def current(self):
        self._sync()
        return self.elapsed

    @staticmethod
    def format(seconds):
        total = int(seconds)
        h = total // 3600
        m = (total % 3600) // 60
        s = total % 60
        return f"{h:02d}", f"{m:02d}", f"{s:02d}"
