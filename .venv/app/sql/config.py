import os
from configparser import ConfigParser

def find_file(start_dir, filename):
    for root, dirs, files in os.walk(start_dir):
        if filename in files:
            return os.path.join(root, filename)
    return None

def load_config(start_dir='.', filename='database.ini', section='postgresql'):
    file_path = find_file(start_dir, filename)
    if file_path is None:
        raise Exception(f'File {filename} not found in directory {start_dir}')
    
    parser = ConfigParser()
    parser.read(file_path)

    # get section, default to postgresql
    config = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            config[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, file_path))

    return config

if __name__ == '__main__':
    config = load_config()
    print(config)
