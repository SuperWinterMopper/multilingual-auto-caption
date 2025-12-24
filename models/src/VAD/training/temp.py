from pathlib import Path

def main():
    backend_model_root = Path(__file__).resolve().parent.parent.parent.parent.parent / "backend" / "model"
    
    print(f"Root directory is: {backend_model_root}")
    
    
    
if __name__ == '__main__':
    main()