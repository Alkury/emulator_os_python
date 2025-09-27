import os
import configparser
import shlex
import sys
import argparse
import csv


path_now =  "~#"
parser = argparse.ArgumentParser()

parser.add_argument('--config', '-c', default='/Users/alkury/PycharmProjects/emulator_os_python/configpath.ini')
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

fs_config = {}

with open(ini_phys, newline="", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        section = row["section"].strip()
        dirs = [d.strip() for d in row.get("dirs", "").split(",") if d.strip()]
        files = [f.strip() for f in row.get("files", "").split(",") if f.strip()]
        fs_config[section] = {"dirs": dirs, "files": files}


def ls_func(path: list, more_data=None):
    section = ".".join(path) if path else "root"
    if path == "~#":
        section = "root"
    if section not in fs_config:
        print(f"ls: cannot access '{more_data}': No such file or directory")
        return None

    dirs = fs_config[section]["dirs"]
    files = fs_config[section]["files"]
    dirs_files = [d + "/" for d in dirs] + files
    return dirs_files


def test_to_dir(path: list):
    section = ".".join(path) if path else "root"
    return section in fs_config


def get_path(name: str):
    return config['paths'][name]

def process_functions(args_input: list):
    global path_now
    if args_input[0] == "exit":
        if len(args_input) == 1:
            sys.exit(0)

    elif "cd" in args_input:
        if len(args_input) == 2:
            if args_input[1] == "..":
                path_not_now = "/".join(path_now.split("/")[:-1]) + "#"
                if path_not_now == "~/#":
                    path_not_now = "~#"
                path_k = path_not_now[:-1].split("/")
                path_k[0] = "root"
                if not test_to_dir(path_k):
                    print(f"-bash: cd: {args_input[1]}: No such file or directory")
                    sys.exit(1)
                else:
                    path_now = path_not_now
            else:
                path_not_now = path_now[:-1] + "/" + args_input[1] + "#"
                path_k = path_not_now[:-1].split("/")
                path_k[0] = "root"
                if not test_to_dir(path_k):
                    print(f"-bash: cd: {args_input[1]}: No such file or directory")
                    sys.exit(1)
                else:
                    path_now = path_not_now
        elif len(args_input) == 1:
            path_now = "~#"
        else:
            print(f"-bash: cd: too many arguments")
            sys.exit(1)

    elif "ls" in args_input:
        if len(args_input) == 1:
            paths = [path_now[:-1].split("/")]
        else:
            paths = []
            for raw in args_input[1:]:
                paths.append(path_now[:-1].split("/") + raw.split("/"))
        for idx, path_k in enumerate(paths):
            path_k[0] = "root"
            cur_dir = ls_func(path_k, "/".join(path_k[1:]))

            if cur_dir:
                if len(paths) > 1:
                    print(f"{'/'.join(path_k[1:])}:")
                for item in cur_dir:
                    print(item)
                if len(paths) > 1 and idx < len(paths) - 1:
                    print()
            else:
                continue
    elif "start" in args_input:
        if len(args_input) == 1:
            print(start_path)
    elif "phys" in args_input:
        if len(args_input) == 1:
            print(phys_path)

    else:
        print(f"{args_input[0]}: command not found")
        sys.exit(1)


def run_script(script_path: str):
    if not os.path.exists(script_path):
        print(f"ERROR: Startup script '{script_path}' not found.")
        sys.exit(1)

    with open(script_path, "r", encoding="utf-8") as f:
        for line in f:
            cmd = line.strip()
            if not cmd or cmd.startswith("#"):  # пропускаем пустые и комментированные строки
                continue

            # выводим как будто пользователь ввёл вручную
            login = config["login data"]["login"]
            hostname = config["login data"]["hostname"]
            prompt = f"{login}@{hostname}:{path_now} "
            print(f"{prompt}{cmd}")

            args_input = shlex.split(cmd)
            try:
                process_functions(args_input)
            except SystemExit as e:
                if e.code != 0:  # ошибка → прерываем выполнение
                    print(f"ERROR while executing startup script: {cmd}")
                    sys.exit(e.code)
                else:
                    sys.exit(0)

if start_path:
    run_script(start_path)

while True:
    path_local = os.getcwd()
    # print(f"Testing {path_local}")
    login = config["login data"]["login"]
    hostname = config["login data"]["hostname"]
    prompt = f"{login}@{hostname}:{path_now} "
    try:
        test_inp = input(prompt)
    except EOFError:
        sys.exit(0)

    args_input = shlex.split(test_inp)
    process_functions(args_input)




