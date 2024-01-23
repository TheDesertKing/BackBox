import json


def write_to_file(path,content):
    with open(path,'wt') as file:
        file.write(content)


class Conf:
    def __init__(self, machine_ip, username, password):
        self.machine_ip = machine_ip
        self.username = username
        self.password = password
        self.machine_url = f"https://{machine_ip}/"


def read_conf_file(path):
    with open(path, 'rt') as conf_file:
        conf_data = json.load(conf_file)

    return Conf(conf_data['MACHINE_IP'],conf_data['USERNAME'],conf_data['PASSWORD'])

