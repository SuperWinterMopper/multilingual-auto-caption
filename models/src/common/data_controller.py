import os
from pathlib import Path
import boto3
from botocore.exceptions import ClientError
import argparse

BUCKET_NAME = 'multilingual-auto-caption'
s3 = boto3.client("s3")


def _resolve_src_dir(root: str) -> Path:
    """Resolve the local directory that corresponds to `models/src`.

    The caller may pass various roots (repo root, `models/`, `models/src`, etc.).
    We pick the first directory that looks like `models/src` by checking for
    expected subfolders.
    """

    def looks_like_models_src(path: Path) -> bool:
        return (path / 'VAD').is_dir() and (path / 'common').is_dir()

    root_path = Path(root).expanduser().resolve()

    # Common direct cases.
    direct_candidates = [
        root_path,
        root_path / 'src',
        root_path / 'models' / 'src',
        root_path / 'models/src',
    ]
    for candidate in direct_candidates:
        if looks_like_models_src(candidate):
            return candidate

    # If `root` points somewhere inside the repo, walk up a bit and re-check.
    for parent in [root_path, *root_path.parents][:6]:
        for candidate in (parent / 'models' / 'src', parent / 'src', parent):
            if looks_like_models_src(candidate):
                return candidate

    # Fallback: relative to this file (models/src/common/data_controller.py).
    return Path(__file__).resolve().parents[1]

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
    src_dir = _resolve_src_dir(root)

    vad_data_root = src_dir / 'VAD' / 'data' / 'LibriParty'

    if not vad_data_root.exists():
        print(f"VAD data directory not found: {vad_data_root}")
        return False

    try:
        for root, _, files in os.walk(vad_data_root):
            for fname in files:
                local_path = Path(root) / fname
                # Keep structure under 'src/...'
                rel_from_src = local_path.relative_to(src_dir)  # e.g., VAD/data/LibriParty/...
                s3_key = f"src/{rel_from_src.as_posix()}"

                s3.upload_file(str(local_path), BUCKET_NAME, s3_key)
                print(f"Uploaded {local_path} -> s3://{BUCKET_NAME}/{s3_key}")
    except ClientError as e:
        print(f"S3 upload failed: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error during upload: {e}")
        return False
    return True

def load_s3_training_data(model: str, root: str) -> bool:
    """Download training data from S3 into the same on-disk layout used by upload.

    For now, this is only implemented for the VAD model.

    Upload stores objects under the `src/` prefix, preserving the local path
    relative to `models/src`. This function reverses that mapping.

    Args:
        model: The model name to download data for (currently only 'VAD').
        root: Workspace/repo root (or `models/src`) used to decide where to write.

    Returns:
        True if all files were downloaded successfully, False otherwise.
    """

    if model.strip().lower() != 'vad':
        raise NotImplementedError("load_s3_training_data is only implemented for the VAD model right now.")

    src_dir = _resolve_src_dir(root)
    prefix = 'src/VAD/data/LibriParty/'

    try:
        paginator = s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=BUCKET_NAME, Prefix=prefix)

        found_any = False
        for page in pages:
            contents = page.get('Contents', [])
            for obj in contents:
                key = obj.get('Key')
                if not key or key.endswith('/'):
                    continue

                found_any = True

                rel_from_src = key[len('src/'):]
                local_path = src_dir / Path(rel_from_src)
                local_path.parent.mkdir(parents=True, exist_ok=True)

                s3.download_file(BUCKET_NAME, key, str(local_path))
                print(f"Downloaded s3://{BUCKET_NAME}/{key} -> {local_path}")

        if not found_any:
            print(f"No objects found in s3://{BUCKET_NAME}/{prefix}")
            return False

    except ClientError as e:
        print(f"S3 download failed: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error during download: {e}")
        return False
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--model', required=True, help="Which model data to upload/download: VAD, SLID, ASR")
    parser.add_argument('-r', '--root', required=True, help="Root directory to save the data")
    parser.add_argument('--upload', action='store_true', help="Upload data to S3 instead of downloading")
    args = parser.parse_args()
    
    if args.upload:
        success = upload_s3_training_data(args.model, args.root)
        if not success:
            print("Upload failed.")
        else:
            print("Upload completed successfully.")
    else:
        success = load_s3_training_data(args.model, args.root)
        if not success:
            print("Download failed.")
        else:
            print("Download completed successfully.")
        
if __name__ == '__main__':
    main()