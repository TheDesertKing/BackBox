import json
import requests
from urllib3.exceptions import InsecureRequestWarning

CONF_FILE_PATH = './conf/88.json'
ICY_PATH = "./icy/"
ICC_PATH = "./icc/"
COMPILED_PATH = "./compiled/"
MAP_FILE_PATH = "./signature_data.map"

# Suppress the warnings from urllib3
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


def backbox_login(conf):
    sess = requests.Session()
    try:
        sess.get(conf.machine_url,verify=False)
    except:
        print(f"can't connect to backbox machine {conf.machine_ip}")
        exit(101)

    login_response = sess.post(conf.machine_url+f"j_security_check",data=f"j_username={conf.username}&j_password={conf.password}",headers={"Content-Type":"application/x-www-form-urlencoded; charset=utf-8"},verify=False)
    if "network" not in login_response.text:
		# If "network" isn't in the response, the login failed and we weren't redirected to the app
        print(f"wrong credentials {conf.machine_ip}")
        exit(102)

    return sess


def write_to_file(path,content):
    with open(path,'wt') as file:
        file.write(content)


class Conf:
    def __init__(self, machine_ip, username, password):
        self.machine_ip = machine_ip
        self.username = username
        self.password = password
        self.machine_url = f"https://{machine_ip}/"


def read_conf_file(path=CONF_FILE_PATH):
    with open(path, 'rt') as conf_file:
        conf_data = json.load(conf_file)

    return Conf(conf_data['MACHINE_IP'],conf_data['USERNAME'],conf_data['PASSWORD'])

