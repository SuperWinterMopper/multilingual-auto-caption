import subprocess
from pathlib import Path

def install_dataset():
    data_root = Path(__file__).parent

    subprocess.run(["wget", "-i", "data/voxforge_urls.txt", "-x", "-P", str(data_root)], check=True)

def main():
    install_dataset()

if __name__ == '__main__':
    main()