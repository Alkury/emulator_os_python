import csv
import io
import os
import base64

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


def file_exists(path_parts: list):
    if not path_parts:
        return False
    
    filename = path_parts[-1]
    dir_parts = path_parts[:-1]
    section = ".".join(dir_parts) if dir_parts else "root"
    
    if section not in fs_config:
        return False
    
    return filename in fs_config[section]["files"]


def dir_exists(path_parts: list):
    section = ".".join(path_parts) if path_parts else "root"
    return section in fs_config


def get_file_content(path_parts: list):
    """Получает содержимое файла"""
    if not file_exists(path_parts):
        return None
    
    filename = path_parts[-1]
    dir_parts = path_parts[:-1]
    section = ".".join(dir_parts) if dir_parts else "root"
    
    content_data = fs_config[section].get("content", {})
    return content_data.get(filename, "")


def add_file(path_parts: list, content: str = ""):
    if not path_parts:
        return False
    
    filename = path_parts[-1]
    dir_parts = path_parts[:-1]
    section = ".".join(dir_parts) if dir_parts else "root"
    
    if section not in fs_config:
        return False
    
    if filename not in fs_config[section]["files"]:
        fs_config[section]["files"].append(filename)
    
    if "content" not in fs_config[section]:
        fs_config[section]["content"] = {}
    
    if content:
        encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
        fs_config[section]["content"][filename] = encoded_content
    else:
        fs_config[section]["content"][filename] = ""
    
    return True


def remove_file(path_parts: list):
    if not file_exists(path_parts):
        return False
    
    filename = path_parts[-1]
    dir_parts = path_parts[:-1]
    section = ".".join(dir_parts) if dir_parts else "root"
    
    fs_config[section]["files"].remove(filename)
    
    if "content" in fs_config[section] and filename in fs_config[section]["content"]:
        del fs_config[section]["content"][filename]
    
    return True


def copy_file(src_path: list, dst_path: list):
    if not file_exists(src_path):
        return False
    
    content = get_file_content(src_path)
    if content is None:
        return False
    
    try:
        decoded_content = base64.b64decode(content).decode("utf-8")
    except:
        decoded_content = ""
    
    return add_file(dst_path, decoded_content)


def move_file(src_path: list, dst_path: list):
    if not copy_file(src_path, dst_path):
        return False
    
    return remove_file(src_path)


def save_fs_to_csv(csv_path: str):
    try:
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['section', 'dirs', 'files', 'content']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for section, data in fs_config.items():
                dirs_str = ','.join(data.get('dirs', []))
                files_str = ','.join(data.get('files', []))
                
                content_list = []
                for filename in data.get('files', []):
                    content_data = data.get('content', {})
                    content_list.append(content_data.get(filename, ''))
                content_str = ','.join(content_list)
                
                writer.writerow({
                    'section': section,
                    'dirs': dirs_str,
                    'files': files_str,
                    'content': content_str
                })
        return True
    except Exception as e:
        print(f"Error saving filesystem: {e}")
        return False