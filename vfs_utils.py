fs_config = {}

def ls_func(path: list, more_data=None):
    section = ".".join(path) if path else "root"
    if path == "~#":
        section = "root"
    if section not in fs_config:
        print(f"ls: cannot access '{more_data}': No such file or directory")
        return None

    dirs = fs_config[section]["dirs"]
    files = fs_config[section]["files"]
    return [d + "/" for d in dirs] + files


def test_to_dir(path: list):
    section = ".".join(path) if path else "root"
    return section in fs_config