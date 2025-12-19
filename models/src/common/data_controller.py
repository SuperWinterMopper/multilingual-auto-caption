import logging
import os
from pathlib import Path
import boto3
from botocore.exceptions import ClientError
import argparse

BUCKET_NAME = 'multilingual-auto-caption'

def upload_s3_training_data(model: str, root: str) -> bool:
    """Upload training data to S3.

    It walks the local directory uploads all files to the S3 bucket,
    preserving the same path structure under the `src/` prefix.

    Args:
        model: The model name to upload data for. 
        root: Workspace/repo root (or `models/src`) used to locate the data on disk.

    Returns:
        True if all files were uploaded successfully, False otherwise.
    """

    s3 = boto3.client('s3')

    root_path = Path(root).resolve()

    # Allow passing either the repo root or the models/src directory.
    if (root_path / 'VAD').exists() and (root_path / 'common').exists():
        src_dir = root_path
    elif (root_path / 'models' / 'src').exists():
        src_dir = root_path / 'models' / 'src'
    elif (root_path / 'src').exists() and (root_path / 'src' / 'VAD').exists():
        src_dir = root_path / 'src'
    else:
        # Fallback to current-file-relative resolution for safety.
        src_dir = Path(__file__).resolve().parent.parent  # models/src

    vad_data_root = src_dir / 'VAD' / 'data' / 'LibriParty'

    if not vad_data_root.exists():
        logging.error(f"VAD data directory not found: {vad_data_root}")
        return False

    try:
        for root, _, files in os.walk(vad_data_root):
            for fname in files:
                local_path = Path(root) / fname
                # Keep structure under 'src/...'
                rel_from_src = local_path.relative_to(src_dir)  # e.g., VAD/data/LibriParty/...
                s3_key = f"src/{rel_from_src.as_posix()}"

                s3.upload_file(str(local_path), BUCKET_NAME, s3_key)
                logging.info(f"Uploaded {local_path} -> s3://{BUCKET_NAME}/{s3_key}")
    except ClientError as e:
        logging.error(f"S3 upload failed: {e}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error during upload: {e}")
        return False

    return True

def load_s3_training_data():
    pass

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--model', required=True, help="Which model data to upload/download: VAD, SLID, ASR")
    parser.add_argument('-r', '--root', required=True, help="Root directory to save the data")
    parser.add_argument('--upload', action='store_true', help="Upload data to S3 instead of downloading")
    args = parser.parse_args()
    
    if args.upload:
        success = upload_s3_training_data(args.model, args.root)
        if not success:
            logging.error("Upload failed.")
        else:
            logging.info("Upload completed successfully.")
    else:
        logging.info("Download path not implemented in this command.")
if __name__ == '__main__':
    main()