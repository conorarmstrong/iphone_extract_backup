import os
import sqlite3
import shutil
import argparse
from tqdm import tqdm

def parse_arguments():
    parser = argparse.ArgumentParser(description='Extract iPhone backup files based on Manifest.db')
    parser.add_argument('backup_folder', help='Path to the iPhone backup folder containing Manifest.db')
    parser.add_argument('-o', '--output', default='extracted', help='Output directory for extracted files (default: extracted)')
    parser.add_argument('--no-progress', action='store_true', help='Disable progress bar')
    return parser.parse_args()

def connect_manifest_db(manifest_path):
    if not os.path.exists(manifest_path):
        raise FileNotFoundError(f"Manifest.db not found at {manifest_path}")
    conn = sqlite3.connect(manifest_path)
    return conn

def fetch_files(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT fileID, relativePath FROM Files")
    return cursor.fetchall()

def copy_files(backup_folder, extracted_folder, files, show_progress=True):
    if not os.path.exists(extracted_folder):
        os.makedirs(extracted_folder)

    iterator = tqdm(files, desc="Copying files") if show_progress else files

    for fileID, relativePath in iterator:
        # Construct source file path
        subfolder = fileID[:2]
        source_file = os.path.join(backup_folder, subfolder, fileID)

        # Construct destination file path
        destination_file = os.path.join(extracted_folder, relativePath)
        destination_dir = os.path.dirname(destination_file)

        try:
            if not os.path.exists(source_file):
                print(f"Warning: Source file not found: {source_file}")
                continue

            if not os.path.exists(destination_dir):
                os.makedirs(destination_dir, exist_ok=True)

            shutil.copy2(source_file, destination_file)
        except Exception as e:
            print(f"Error copying {source_file} to {destination_file}: {e}")

def main():
    args = parse_arguments()

    backup_folder = args.backup_folder
    extracted_folder = args.output
    show_progress = not args.no_progress

    manifest_path = os.path.join(backup_folder, 'Manifest.db')

    print(f"Connecting to Manifest.db at {manifest_path}...")
    try:
        conn = connect_manifest_db(manifest_path)
    except FileNotFoundError as e:
        print(e)
        return

    print("Fetching file list from Manifest.db...")
    try:
        files = fetch_files(conn)
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return
    finally:
        conn.close()

    print(f"Total files to copy: {len(files)}")
    print(f"Starting extraction to '{extracted_folder}'...")

    copy_files(backup_folder, extracted_folder, files, show_progress=show_progress)

    print("Extraction completed.")

if __name__ == "__main__":
    main()
