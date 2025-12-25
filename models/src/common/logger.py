from pydantic import BaseModel, Field
import time
from pathlib import Path
from datetime import datetime
import torch
import matplotlib.pyplot as plt
import threading

class Logger(BaseModel):
    name: str
    t_start: float = Field(default_factory=time.perf_counter)
    start_time: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    output_path_root: Path = Path(__file__).resolve().parent
    vad_accuracy_history_plot_path: Path = output_path_root / "vad_accuracy_history.png"
    
    # asynchornously prints heartbeat log, stops execution once program stops executing
    def heartbeat_log(self, interval: int):
        while True:
            self.log("Heartbeat (Program is running)")
            time.sleep(interval)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        thread = threading.Thread(target=self.heartbeat_log, args=(60,), daemon=True)
        thread.start()

    def log(self, text):
        path = self.output_path_root / f"{self.name}.txt"
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"[{self.start_time}] {self.name} | {(time.perf_counter() - self.t_start):.2f}s: {text}\n")
    
    def log_spectrogram(self, spectrograms: torch.Tensor, name: str, num_mel_bands: int) -> None:
        assert spectrograms.dim() == 3, "Spectrogram must be 3D tensor"
        assert spectrograms.shape[1] == num_mel_bands and spectrograms.shape[2] == num_mel_bands, "Attempting to log spectrogram with incorrect dimensions"
        
        N = spectrograms.shape[0]
        
        fig, axes = plt.subplots(1, N, figsize=(4 * N, 4))
        if N == 1:
            axes = [axes]
        
        for i in range(N):
            spec = spectrograms[i].cpu().numpy()
            im = axes[i].imshow(spec, aspect='auto', origin='lower', cmap='viridis')
            axes[i].set_title(f'Sample {i+1}')
            axes[i].set_xlabel('Time')
            axes[i].set_ylabel('Mel Band')
            plt.colorbar(im, ax=axes[i])
        
        plt.tight_layout()
        
        output_path = self.output_path_root / f"{name}.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        
        self.log(f"Saved spectrogram visualization to {output_path}")
    
    def log_training_graph(self, train_acc_hist, valid_acc_hist):
        epochs = list(range(1, len(train_acc_hist) + 1))

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(epochs, train_acc_hist, label="Train")
        ax.plot(epochs, valid_acc_hist, label="Validation")
        ax.set_xlabel("Epoch")
        ax.set_ylabel("Accuracy")
        ax.set_title("Training / Validation Accuracy")
        ax.set_ylim(0.0, 1.0)
        ax.grid(True, alpha=0.3)
        ax.legend()
        fig.tight_layout()

        output_path = self.vad_accuracy_history_plot_path
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        
        self.log(f"Saved training accuracy history plot to {output_path}")