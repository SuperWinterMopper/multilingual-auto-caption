import logging
import datetime
from pathlib import Path
import threading
import psutil

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
        process = psutil.Process()
        while not self._stop_event.is_set():
            self.logger.info('Heartbeat: program/logger is running')
            # Memory usage
            mem_info = process.memory_info()
            total_mem = psutil.virtual_memory().total
            mem_used_gb = mem_info.rss / (1024 ** 3)
            total_mem_gb = total_mem / (1024 ** 3)
            self.logger.info(f'Memory: {mem_used_gb:.2f} GB / {total_mem_gb:.2f} GB')
            
            # CPU usage
            cpu_percent = process.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            if cpu_count:
                self.logger.info(f'CPU: {cpu_percent:.2f}% / {cpu_count * 100}%')
            else:
                self.logger.info(f'CPU: {cpu_percent:.2f}%')
            
            # Disk usage
            disk_usage = psutil.disk_usage('/')
            disk_used_gb = disk_usage.used / (1024 ** 3)
            disk_total_gb = disk_usage.total / (1024 ** 3)
            self.logger.info(f'Disk: {disk_used_gb:.2f} GB / {disk_total_gb:.2f} GB')
            
            # sleep in a stoppable way
            self._stop_event.wait(interval)

    def stop(self):
        self._stop_event.set()
        # optional: wait briefly for it to finish
        if self._heartbeat_thread.is_alive():
            self._heartbeat_thread.join(timeout=1)