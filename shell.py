# shell.py
import sys
from vfs_utils import *

class Shell:
    def __init__(self, vfs_name, vfs_hash, start_path, phys_path, login, hostname):
        self.path_now = "~#"
        self.vfs_name = vfs_name
        self.vfs_hash = vfs_hash
        self.start_path = start_path
        self.phys_path = phys_path
        self.login = login
        self.hostname = hostname

    def get_prompt(self):
        return f"{self.login}@{self.hostname}:{self.path_now} "

    def run_command(self, args_input: list):
        if not args_input:
            return
        cmd, *args = args_input
        method = getattr(self, f"cmd_{cmd.replace('-', '_')}", None)
        if method:
            method(args)
        else:
            print(f"{cmd}: command not found")

    def cmd_exit(self, args_input):
        if len(args_input) == 0:
            sys.exit(0)

    def cmd_start(self, args_input):
        if len(args_input) == 0:
            print(self.start_path)

    def cmd_phys(self, args_input):
        if len(args_input) == 0:
            print(self.phys_path)

    def cmd_vfs_info(self, args_input):
        if len(args_input) == 0:
            print(f"VFS name: {self.vfs_name}")
            print(f"SHA-256: {self.vfs_hash}")

    def cmd_cd(self, args_input):
        if len(args_input) == 1:
            if args_input[0] == "..":
                path_not_now = "/".join(self.path_now.split("/")[:-1]) + "#"
                if path_not_now == "~/#":
                    path_not_now = "~#"
                path_k = path_not_now[:-1].split("/")
                path_k[0] = "root"
                if not test_to_dir(path_k):
                    print(f"-bash: cd: {args_input[0]}: No such file or directory")
                    sys.exit(1)
                else:
                    self.path_now = path_not_now
            else:
                path_not_now = self.path_now[:-1] + "/" + args_input[0] + "#"
                path_k = path_not_now[:-1].split("/")
                path_k[0] = "root"
                if not test_to_dir(path_k):
                    print(f"-bash: cd: {args_input[0]}: No such file or directory")
                    sys.exit(1)
                else:
                    self.path_now = path_not_now
        elif len(args_input) == 0:
            self.path_now = "~#"
        else:
            print(f"-bash: cd: too many arguments")
            sys.exit(1)

    def cmd_ls(self, args_input):
        if len(args_input) == 0:
            paths = [self.path_now[:-1].split("/")]
        else:
            paths = []
            for raw in args_input:
                paths.append(self.path_now[:-1].split("/") + raw.split("/"))
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

    def cmd_cat(self, args_input):
        if len(args_input) < 1:
            print("cat: missing file operand")
            return

        filepath = args_input[0].strip()

        if filepath.startswith("/"):
            path_parts = ["root"] + [p for p in filepath.strip("/").split("/") if p]
        else:
            current_path = self.path_now[:-1].split("/")
            current_path[0] = "root"
            path_parts = current_path + [p for p in filepath.split("/") if p]

        filename = path_parts[-1]
        dir_parts = path_parts[:-1]
        section = ".".join(dir_parts) if dir_parts else "root"

        if section not in fs_config:
            print(f"cat: {filepath}: No such file or directory")
            return

        files = fs_config[section]["files"]
        content_data = fs_config[section].get("content", {})

        if filename not in files:
            print(f"cat: {filepath}: No such file or directory")
            return

        if filename in content_data and content_data[filename]:
            try:
                import base64
                decoded_content = base64.b64decode(content_data[filename])
                try:
                    print(decoded_content.decode("utf-8"))
                except UnicodeDecodeError:
                    print(f"Binary file (size: {len(decoded_content)} bytes)")
                    print(f"Base64: {content_data[filename]}")
            except Exception as e:
                print(f"cat: error reading {filepath}: {e}")
        else:
            print(f"cat: {filepath}: file has no content")

    def cmd_find(self, args_input):
        if not args_input:
            print("find: missing file operand")
            return

        target_name = args_input[0]

        if len(args_input) > 1:
            start_path = args_input[1]
        else:
            start_path = self.path_now[:-1]

        if start_path in ("~", "~#"):
            dir_parts = ["root"]
        elif start_path.startswith("/"):
            dir_parts = ["root"] + [p for p in start_path.strip("/").split("/") if p]
        else:
            current_path = self.path_now[:-1].split("/")
            current_path[0] = "root"
            dir_parts = current_path + [p for p in start_path.split("/") if p]

        start_section = ".".join(dir_parts) if dir_parts else "root"

        if start_section not in fs_config:
            print(f"find: {start_path}: No such file or directory")
            return

        def recursive_find(section, path_so_far):
            found = []
            entry = fs_config.get(section, {})

            for f in entry.get("files", []):
                if f == target_name:
                    found.append(f"{path_so_far}/{f}")

            for d in entry.get("dirs", []):
                if d == target_name:
                    found.append(f"{path_so_far}/{d}")
                sub_section = section + "." + d
                found.extend(recursive_find(sub_section, f"{path_so_far}/{d}"))

            return found

        results = recursive_find(start_section, "/" + "/".join(dir_parts[1:]))

        if results:
            for r in results:
                if r[0] == r[1] == '/':
                    r = '.' + r[1:]
                print(r)
        else:
            print(f"find: '{target_name}' not found")

    def cmd_tac(self, args_input):
        if len(args_input) < 1:
            print("tac: missing file operand")
            return

        filepath = args_input[0].strip()

        if filepath.startswith("/"):
            path_parts = ["root"] + [p for p in filepath.strip("/").split("/") if p]
        else:
            current_path = self.path_now[:-1].split("/")
            current_path[0] = "root"
            path_parts = current_path + [p for p in filepath.split("/") if p]

        filename = path_parts[-1]
        dir_parts = path_parts[:-1]
        section = ".".join(dir_parts) if dir_parts else "root"

        if section not in fs_config:
            print(f"tac: {filepath}: No such file or directory")
            return

        files = fs_config[section]["files"]
        content_data = fs_config[section].get("content", {})

        if filename not in files:
            print(f"tac: {filepath}: No such file or directory")
            return

        if filename in content_data and content_data[filename]:
            try:
                import base64
                decoded_content = base64.b64decode(content_data[filename])
                try:
                    print(decoded_content.decode("utf-8")[::-1])
                except UnicodeDecodeError:
                    print(f"Binary file (size: {len(decoded_content)} bytes)")
                    print(f"Base64: {content_data[filename]}")
            except Exception as e:
                print(f"cat: error reading {filepath}: {e}")
        else:
            print(f"cat: {filepath}: file has no content")