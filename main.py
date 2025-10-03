import io
import os
import configparser
import shlex
import sys
import argparse
import csv
import hashlib
import base64

from shell import Shell
from vfs_utils import fs_config

parser = argparse.ArgumentParser()

parser.add_argument('--config', '-c', default='/Users/alkury/PycharmProjects/emulator_os_python/config_files/configpath.ini')
parser.add_argument('--start', '-s')
parser.add_argument('--phys', '-p')

args = parser.parse_args()

config = configparser.ConfigParser()
ini_path = args.config
read_result = config.read(ini_path)

if not read_result:
    print(f"ERROR: Config file not found at '{ini_path}'.")
    sys.exit(1)

ini_phys = config.get('paths', 'phys_path', fallback=None)
ini_start = config.get('paths', 'start_path', fallback=None)

phys_path = args.phys or ini_phys
start_path = args.start or ini_start
config_path = ini_path

try:
    if not os.path.exists(ini_phys):
        print(f"ERROR: VFS file not found at '{ini_phys}'.")
        sys.exit(1)
    
    with open(ini_phys, "r", encoding="utf-8") as f:
        csv_data = f.read()
    
    vfs_hash = hashlib.sha256(csv_data.encode("utf-8")).hexdigest()
    vfs_name = os.path.basename(ini_phys)
    
    parsed_fs_config = {}
    try:
        reader = csv.DictReader(io.StringIO(csv_data))
        for row_num, row in enumerate(reader, start=2):
            if not row.get("section"):
                print(f"ERROR: Invalid VFS format - missing 'section' field in row {row_num}")
                sys.exit(1)
            
            section = row["section"].strip()
            dirs = [d.strip() for d in row.get("dirs", "").split(",") if d.strip()]
            files = [f.strip() for f in row.get("files", "").split(",") if f.strip()]
            content_data = {}
            if "content" in row and row["content"]:
                content_list = [c.strip() for c in row["content"].split(",") if c.strip()]
                for i, file_name in enumerate(files):
                    if i < len(content_list):
                        try:
                            decoded_content = base64.b64decode(content_list[i])
                            content_data[file_name] = content_list[i]
                        except Exception as e:
                            print(f"WARNING: Invalid base64 data for file '{file_name}' in section '{section}': {e}")
                            content_data[file_name] = ""
            
            parsed_fs_config[section] = {"dirs": dirs, "files": files, "content": content_data}
    
    except csv.Error as e:
        print(f"ERROR: Invalid CSV format in VFS file: {e}")
        sys.exit(1)

except IOError as e:
    print(f"ERROR: Cannot read VFS file '{ini_phys}': {e}")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: Unexpected error loading VFS: {e}")
    sys.exit(1)

def get_path(name: str):
    return config['paths'][name]

fs_config.update(parsed_fs_config)
login = config["login data"]["login"]
hostname = config["login data"]["hostname"]
shell = Shell(
        vfs_name=vfs_name,
        vfs_hash=vfs_hash,
        start_path=start_path,
        phys_path=phys_path,
        login=login,
        hostname=hostname
)

def run_script(script_path: str):
    if not os.path.exists(script_path):
        print(f"ERROR: Startup script '{script_path}' not found.")
        sys.exit(1)
    if script_path.endswith(".csv"):
        print(f"ERROR: Startup script '{script_path}' looks like CSV, not a shell script.")
        sys.exit(1)

    with open(script_path, "r", encoding="utf-8") as f:
        for line in f:
            cmd = line.strip()
            if not cmd or cmd.startswith("#"):
                continue

            print(f"{shell.get_prompt()}{cmd}")

            try:
                shell.run_command(cmd.split())
            except SystemExit as e:
                if e.code != 0:
                    print(f"ERROR while executing startup script: {cmd}")
                    sys.exit(e.code)
                else:
                    sys.exit(0)

if start_path:
    run_script(start_path)

if __name__ == "__main__":
    while True:
        try:
            user_input = input(shell.get_prompt())
            if user_input.strip():
                shell.run_command(user_input.split())
        except EOFError:
            sys.exit(0)
        except KeyboardInterrupt:
            print("\nUse 'exit' to quit.")
            continue



