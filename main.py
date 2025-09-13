import os, socket

import shlex
import sys


while True:
    path_local = os.getcwd()
    # print(f"Testing {path_local}")
    if path_local.split("/")[-1] == "emulator_os_python":
        path_now = "~#"
    else:
        path_now = "~" + path_local.split("emulator_os_python")[-1] + "#"
    prompt = f"{os.getlogin()}@{socket.gethostname()}:{path_now} "
    test_inp = input(prompt)
    args_input = shlex.split(test_inp)


    if len(args_input) == 1 and args_input[0] == "exit":
        sys.exit(0)

    if "cd" in args_input and len(args_input) == 2:
        os.chdir(args_input[1])

    if "ls" in args_input and len(args_input) == 1:
        cur_dir = os.getcwd()
        for i in os.listdir(cur_dir):
            print(i)