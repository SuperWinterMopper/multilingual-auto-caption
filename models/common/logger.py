from pydantic import BaseModel
import time
# from pathlib import Path

class Logger(BaseModel):
    dir_path: str
    logger_name: str
    t_start: float
    
    def log(self, text):
        path = self.dir_path + "/" + self.logger_name
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"{self.logger_name} | {(time.perf_counter() - self.t_start):.2f}s: {text}\n")