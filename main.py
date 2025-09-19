import os
import configparser
import shlex
import sys

path_now =  "~#"
config = configparser.ConfigParser()
test_of_read_ini = config.read("configpath.ini")
if not test_of_read_ini:
    print("ERROR: Config file not found.")
    sys.exit(1)  # exit code 1 для ошибки

def ls_func(path: list, more_data=None):
    section = ".".join(path) if path else "root"
    if path == "~#":
        section = "root"
    if section not in config:
        print(f"ls: cannot access '{more_data}': No such file or directory")
        return None

    dirs = [d.strip() for d in config[section].get("dirs", "").split(",") if d.strip()]
    files = [f.strip() for f in config[section].get("files", "").split(",") if f.strip()]
    dirs_files = []
    for d in dirs:
        dirs_files.append(d + "/")
    for f in files:
        dirs_files.append(f)
    return dirs_files


def test_to_dir(path: list):
    section = ".".join(path) if path else "root"
    if section not in config:
        return None
    else:
        return True


def get_path(name: str):
    return config['paths'][name]


while True:
    path_local = os.getcwd()
    # print(f"Testing {path_local}")
    login = config["login data"]["login"]
    hostname = config["login data"]["hostname"]
    prompt = f"{login}@{hostname}:{path_now} "
    test_inp = input(prompt)
    args_input = shlex.split(test_inp)


    if len(args_input) == 1 and args_input[0] == "exit":
        sys.exit(0)

    if "cd" in args_input and len(args_input) == 2:
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


    if "ls" in args_input:
        if len(args_input) == 1:
            path_k = path_now[:-1].split("/")
            args = None
        else:
            path_k = path_now[:-1].split("/") + args_input[1].split("/")
            args = args_input[1]
        path_k[0] = "root"

        cur_dir = ls_func(path_k, args)
        if cur_dir:
            for item in cur_dir:
                print(item)
        else:
            sys.exit(1)

    if "start" in args_input:
        if len(args_input) == 1:
            path_start = get_path("phys_path")
        else:
            path_start = args_input[1]
        print(path_start)

    if "config" in args_input and len(args_input) == 1:
        path_config = get_path("start_path")
        print(path_config)
