import logging
import datetime
from pathlib import Path
import threading
import psutil
import platform
import torch
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from moviepy import VideoFileClip
from ..dataclasses.audio_segment import AudioSegment

class AppLogger():
    def __init__(self, log_suffix, level: int = logging.INFO, prod=False):
        self.logs_dir = Path(__file__).parent.parent.parent / 'logs'
        self.prod = prod
        self.log_root, self.log_file = self.create_log_directory(logs_root=self.logs_dir, log_suffix=log_suffix)
        
        # set up logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler = logging.FileHandler(self.log_file, mode='a')
        file_handler.setFormatter(formatter)
        # prevent duplicate handlers if re-initialized
        self.logger.handlers.clear()
        self.logger.addHandler(file_handler)
        self.logger.propagate = False
        
        # run heartbeat_metrics thread with proper stopping mechanism
        self._stop_event = threading.Event()
        self._heartbeat_thread = threading.Thread(
            target=self.heartbeat_metrics,
            args=(60,),
            daemon=True
        )
        self._heartbeat_thread.start()
        
        self.log_machine_info()
        
        self.logger.info(f'Logger initialized for {self.log_file}')
    
    def log_machine_info(self):
        cpu = psutil.cpu_count
        ram = psutil.virtual_memory().total / (1024**3)
        disk = psutil.disk_usage("/")
        machine_info = (f"CPU: {platform.processor() or platform.uname().processor} | "
                f"Cores: {cpu(False)}, Threads: {cpu(True)} | RAM: {ram:.1f} GB | "
                f"Disk: {disk.used/(1024**3):.1f} GB / {disk.total/(1024**3):.1f} GB used")
        if torch.cuda.is_available():
            g = torch.cuda.get_device_properties(0).total_memory/(1024**3)
            machine_info += f" | GPU: {torch.cuda.get_device_name(0)} ({g:.1f} GB)"
        else:
            machine_info += " | GPU: None"
        self.logger.info(machine_info)
        
    def create_log_directory(self, logs_root: Path, log_suffix: str) -> tuple[Path, Path]:
        logs_root.mkdir(parents=True, exist_ok=True)
        
        root = logs_root / f"{datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}_{log_suffix}"
        root.mkdir(parents=True, exist_ok=True)
        
        log_path = root / "main.log"
        
        if not log_path.exists():
            log_path.touch()
        return root, log_path

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
    
    def log_segments_visualization(self, video: VideoFileClip, audio_segments: list[AudioSegment]):
        if self.prod:
            return  # skip in prod mode
        
        if not audio_segments:
            return
        
        # Validate all segments have the same orig_file
        orig_file = audio_segments[0].orig_file
        if not all(seg.orig_file == orig_file for seg in audio_segments):
            self.logger.warning("Not all audio segments have the same orig_file. Skipping visualization.")
            return
        
        _, ax = plt.subplots(figsize=(12, 4))
        
        # Get unique languages and assign colors
        langs = list(set(seg.lang for seg in audio_segments))
        colors = plt.cm.tab10(range(len(langs)))
        lang_to_color = {lang: colors[i] for i, lang in enumerate(langs)}
        
        # Draw video duration bar at the bottom
        ax.barh(0, video.duration, height=0.5, color='lightgray', edgecolor='black', label='Video Duration')
        
        # Draw audio segment bars
        for i, segment in enumerate(audio_segments, start=1):
            duration = segment.end_time - segment.start_time
            color = lang_to_color[segment.lang]
            ax.barh(i, duration, left=segment.start_time, height=0.5, color=color, edgecolor='black')
        
        # Create legend outside the plot area
        handles = [mpatches.Patch(color=lang_to_color[lang], label=lang) for lang in langs]
        handles.insert(0, mpatches.Patch(color='lightgray', label='Video Duration'))
        ax.legend(handles=handles, loc='upper left', bbox_to_anchor=(1, 1))
        
        # Labels and title
        ax.set_xlabel('Time (seconds)')
        ax.set_title(f'Audio Segments: {orig_file}')
        ax.set_ylim(-0.5, len(audio_segments) + 0.5)
        ax.set_xlim(0, video.duration)
        ax.set_yticks(range(len(audio_segments) + 1))
        ax.set_yticklabels(['Video'] + [f'Segment {i}' for i in range(1, len(audio_segments) + 1)])
        
        # Save figure
        viz_path = self.log_root / f"seg_vis_{datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}.png"
        plt.savefig(viz_path, dpi=100, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Segments visualization saved to {viz_path}")
        
    def log_audio_segments_list(self, audio_segments: list[AudioSegment]):
        N = 3  # number of segments to show from start and end
        max_log_text_len = 20  # max length for text field
        
        if not audio_segments:
            self.logger.info("Audio Segments List: No segments to display")
            return
        
        total = len(audio_segments)
        log_lines = [f"Audio Segments List: {total} total segments"]
        
        def format_segment(seg: AudioSegment, idx: int) -> str:
            text = seg.text
            if len(text) > max_log_text_len:
                text = text[:max_log_text_len-3] + "..."
            return (f"[{idx}] id={seg.id} | {seg.start_time:.2f}s-{seg.end_time:.2f}s | "
                   f"lang={seg.lang} | file={seg.orig_file} | text='{text}'")
        
        for i in range(min(N, total)):
            log_lines.append(format_segment(audio_segments[i], i + 1))
        
        if total > 2 * N:
            log_lines.append(f"... ({total - 2 * N} segments omitted) ...")
        
        if total > N:
            start_idx = max(N, total - N)
            for i in range(start_idx, total):
                log_lines.append(format_segment(audio_segments[i], i + 1))
        
        self.logger.info("\n".join(log_lines))