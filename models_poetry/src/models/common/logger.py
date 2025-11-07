from pydantic import BaseModel, Field
import time
from pathlib import Path
from datetime import datetime

class Logger(BaseModel):
    name: str
    t_start: float = Field(default_factory=time.perf_counter)
    start_time: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def log(self, text):

        path = Path(__file__).resolve().parent / f"{self.name}.txt"
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"[{self.start_time}] {self.name} | {(time.perf_counter() - self.t_start):.2f}s: {text}\n")