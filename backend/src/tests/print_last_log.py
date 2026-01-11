from pathlib import Path

# Number of recent log files to print
K_RECENT_LOGS = 2

def main():
    try:
        logs_dir = Path(__file__).parent.parent.parent / "logs"
        print(f"Expecting at least {K_RECENT_LOGS} logs directory in:", logs_dir)
    except Exception as e:
        print("Error determining logs directory:", str(e))
        return
    
    try:
        print(f"Pringing the {K_RECENT_LOGS} most recent log files...\n")
        recent_logs_dirs = sorted(logs_dir.iterdir(), key=lambda x: x.name)[-K_RECENT_LOGS:]
        for log_dir in recent_logs_dirs:
            logfile = log_dir / "main.log"
            print(f"Printing contents of {logfile}:\n")
            with open(logfile, 'r') as f:
                content = f.read()
                print(content)
    except Exception as e:
        print("Error reading log files:", str(e))
        return

if __name__ == '__main__':
    main()