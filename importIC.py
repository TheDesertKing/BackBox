#!/usr/bin/python3
'''
IMPORTIC.PY

The script will search and download a signature name containing all arguments,
prompting a user to pick if multiple are available.

Usage:

./importIC.py name of signature
(takes multiple arguments)

'''


from sys import argv,exit
import requests
from urllib3.exceptions import InsecureRequestWarning
from json import load

# Suppress the warnings from urllib3
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


SERVER_CONF_PATH="./88.conf.json"
SAVE_PATH = "./icc/"
NAME_MAP_FILE = "./signature_to_filename.map"


def read_conf_file(path):
    with open(SERVER_CONF_PATH, 'rt') as conf_file:
        conf_data = load(conf_file)
    global MACHINE_ADDRESS, USERNAME, PASSWORD, MACHINE_URL
    MACHINE_ADDRESS = conf_data['MACHINE_ADDRESS']
    USERNAME = conf_data['USERNAME']
    PASSWORD = conf_data['PASSWORD']
    MACHINE_URL = f"https://{MACHINE_ADDRESS}/"

def get_signature_name(argv):
    if len(argv) < 2:
        print(f"missing IntelliCheck signature name {MACHINE_ADDRESS}\npython3 importIC.py 'Signaure Name'")
        exit(41)

    return " ".join(argv[1:])


def backbox_login():
    sess = requests.Session()
    try:
        sess.get(MACHINE_URL,verify=False)
    except:
        print(f"can't connect to backbox machine {MACHINE_ADDRESS}")
        exit(42)

    login_response = sess.post(MACHINE_URL+f"j_security_check",data=f"j_username={USERNAME}&j_password={PASSWORD}",headers={"Content-Type":"application/x-www-form-urlencoded; charset=utf-8"},verify=False)
    if "network" not in login_response.text:
		# If "network" isn't in the response, the login failed and we weren't redirected to the app
        print(f"wrong credentials {MACHINE_ADDRESS}")
        exit(43)

    return sess


def get_matching_signatures(signature_name,all_signatures):

    name_search = signature_name.split(' ')

    matching_signatures = [sig for sig in all_signatures.json() if all([search.lower() in sig["name"].lower() for search in name_search])]

    return matching_signatures


def get_signature_data(matching_signatures):
    if len(matching_signatures) == 0:
        print(f"no signature matching the name provided was found {MACHINE_ADDRESS}")
        exit(44)

    elif len(matching_signatures) == 1:
        return matching_signatures[0]

    else:
        signature_names = [sig["name"] for sig in matching_signatures]
        index = 1
        for name in signature_names:
            print(f"[{index}] {name}")
            index += 1

        print(f"please pick signature using it's index (1-{index-1})")

        while True:
            picked_index = input()

            try:
                picked_index = int(picked_index)

            except Exception as e:
                print("index picked is not a number, try again")
                continue

            if picked_index < 1 or picked_index > index-1:
                print("index picked is out of range, try again")

            else:
                return matching_signatures[picked_index-1]


def get_signature_commands(session_id,sess):
    # due to what seems to be a bug, the sessionCommands always seem to be empty
    # so in order to get them we will use another API call using the sessionId we fetched
    return sess.get(MACHINE_URL + f"rest/data/integrator/session/commands/{session_id}",headers={"Accept":"application/json"}).text


def add_names_to_map_file(signature_name,file_name):
    # before saving file, insert file name, signature original name and machine to map file
    with open(NAME_MAP_FILE, 'r+') as map_file:
        map_data = map_file.readlines()
        is_new_sig = True
        if signature_name in [sig_name.split(' | ')[0] for sig_name in map_data]:
            print('Notice: this signature was imported to icy in the past, do you want to continue? ')
            inp = ''
            while inp not in ['y','n']:
                inp = input('[y/n]: ').lower()

            if inp == 'n':
                print('Exiting')
                exit(45)

            else:
                is_new_sig = False

        if is_new_sig:
            new_data_mapping = '\n' + signature_name + ' | ' + file_name + ' | ' + MACHINE_ADDRESS
            map_file.write(new_data_mapping)


def write_to_file(signature_name,commands):
    # remove characters that might cause issues in file names
    bad_chars = ['>',':','/','*','\\','<',':','|','?']
    file_name = signature_name
    for char in bad_chars:
        file_name = file_name.replace(char,"")

    add_names_to_map_file(signature_name,file_name)

    with open(SAVE_PATH + file_name + '.icc','wt') as file:
        file.write(commands)

    print('\n' + file_name + ' was saved successfully')


def main():
    read_conf_file(SERVER_CONF_PATH)

    print("server: " + MACHINE_ADDRESS + "\n")

    signature_name = get_signature_name(argv)

    sess = backbox_login()

    all_signatures = sess.get(MACHINE_URL+"rest/data/intelliChecks/signatures/0/true",headers={"Accept":"application/json"})

    matching_signatures = get_matching_signatures(signature_name,all_signatures)

    signature_data = get_signature_data(matching_signatures)

    signature_commands = get_signature_commands(signature_data['sessionId'],sess)

    write_to_file(signature_data["name"],signature_commands)


main()

