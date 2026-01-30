import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--prod",
        action="store_true",
        help="Run the app in production mode (makes it not store large files on disk, just text and image log files)",
    )

    args = parser.parse_args()
    PROD = args.prod
    if PROD:
        print("Running in PRODUCTION mode")
    else:
        print("Running in DEVELOPMENT mode")


if __name__ == "__main__":
    main()
