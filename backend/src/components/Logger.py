import logging
import datetime
from pathlib import Path

class AppLogger():
    def __init__(self, log_prefix, level: int = logging.INFO):
        self.logs_root = Path(__file__).parent.parent.parent / 'logs'
        
        self.log_file = self.create_log_directory(root_path=self.logs_root, log_prefix=log_prefix)
        logging.basicConfig(
            filename=str(self.log_file),
            filemode='a',
            format='%(asctime)s - %(levelname)s - %(message)s',
            level=level
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f'Logger initialized for {self.log_file}')
    
    def create_log_directory(self, root_path: Path, log_prefix: str) -> Path:
        root_path.mkdir(parents=True, exist_ok=True)
        
        path = root_path / f"{Path(log_prefix).stem}_{datetime.datetime.now().strftime('%Y%m%d')}.log"
        if not path.exists():
            path.touch()
        return path