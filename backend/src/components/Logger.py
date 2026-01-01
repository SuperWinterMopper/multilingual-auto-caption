import logging
import datetime
from pathlib import Path
import threading
import psutil
import platform
import torch
from moviepy import VideoFileClip

class AppLogger():
    def __init__(self, log_prefix, level: int = logging.INFO, prod=False):
        self.logs_root = Path(__file__).parent.parent.parent / 'logs'
        
        self.set_new_log_file(log_prefix=log_prefix)
        
        logging.basicConfig(
            filename=str(self.log_file),
            filemode='a',
            format='%(asctime)s - %(levelname)s - %(message)s',
            level=level
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f'Logger initialized for {self.log_file}')
        
        # run heartbeat_metrics thread with proper stopping mechanism
        self._stop_event = threading.Event()
        self._heartbeat_thread = threading.Thread(
            target=self.heartbeat_metrics,
            args=(60,),
            daemon=True
        )
        self._heartbeat_thread.start()
        
        self.log_machine_info()
    
    def log_machine_info(self):
        cpu = psutil.cpu_count
        ram = psutil.virtual_memory().total / (1024**3)
        disk = psutil.disk_usage("/")
        machine_info = (f"CPU: {platform.processor() or platform.uname().processor} | "
                f"Cores: {cpu(False)}, Threads: {cpu(True)} | RAM: {ram:.1f} GB | "
                f"Disk: {disk.total/(1024**3):.1f} GB/{disk.used/(1024**3):.1f} GB used")
        if torch.cuda.is_available():
            g = torch.cuda.get_device_properties(0).total_memory/(1024**3)
            machine_info += f" | GPU: {torch.cuda.get_device_name(0)} ({g:.1f} GB)"
        else:
            machine_info += " | GPU: None"
        self.logger.info(machine_info)
        
    def set_new_log_file(self, log_prefix: str):
        self.log_file = self.create_log_directory(logs_root=self.logs_root, log_prefix=log_prefix)

    def create_log_directory(self, logs_root: Path, log_prefix: str) -> Path:
        logs_root.mkdir(parents=True, exist_ok=True)
        
        root = logs_root / f"{Path(log_prefix).stem}_{datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}"
        root.mkdir(parents=True, exist_ok=True)
        
        log_path = root / "main.log"
        
        if not log_path.exists():
            root.touch()
        return log_path

    def heartbeat_metrics(self, interval: int):
        while not self._stop_event.is_set():
            self.logger.info("Heartbeat: logger is running")
            self.log_metrics_snapshot()
            
            # sleep in a stoppable way
            self._stop_event.wait(interval)

    def stop(self):
        self._stop_event.set()
        # optional: wait briefly for it to finish
        if self._heartbeat_thread.is_alive():
            self.logger.info("Stopping heartbeat thread (should have no more heartbeats)")
            self._heartbeat_thread.join(timeout=1)

    def log_metrics_snapshot(self):
        process = psutil.Process()
        
        snapshot = "Metrics Snapshot: "
        
        # Memory usage
        mem_info = process.memory_info()
        total_mem = psutil.virtual_memory().total
        mem_used_gb = mem_info.rss / (1024 ** 3)
        total_mem_gb = total_mem / (1024 ** 3)
        snapshot += f' | Memory: {mem_used_gb:.2f} GB / {total_mem_gb:.2f} GB'
        
        # CPU usage
        cpu_percent = process.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        if cpu_count:
            snapshot += f' | CPU: {cpu_percent:.2f}% / {cpu_count * 100}%'
        else:
            snapshot += f' | CPU: {cpu_percent:.2f}%'
        
        # Disk usage
        disk_usage = psutil.disk_usage('/')
        disk_used_gb = disk_usage.used / (1024 ** 3)
        disk_total_gb = disk_usage.total / (1024 ** 3)
        snapshot += f' | Disk: {disk_used_gb:.2f} GB / {disk_total_gb:.2f} GB'
        
        self.logger.info(snapshot)
    
    def log_video_metrics(self, video: VideoFileClip):
        self.logger.info(f"Video Metrics: duration={video.duration}s, fps={video.fps}, size={video.size}")