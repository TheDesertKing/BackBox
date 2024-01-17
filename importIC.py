#!/usr/bin/python3
'''
IMPORTIC.PY

The script will search and download a signature name containing all arguments,
prompting a user to pick if multiple are available.

Usage:

./importIC.py name of signature
(takes multiple arguments)

'''

# For debugging
from icecream import ic

from sys import argv,exit
import requests
from urllib3.exceptions import InsecureRequestWarning
from json import load

# Suppress the warnings from urllib3
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


SERVER_CONF_PATH="./conf/88.json"
SAVE_PATH = "./icc/"
SIGNATURE_DATA_FILE = "./signature_data.map"


def write_to_file(path,content):
    with open(path,'wt') as file:
        file.write(content)


def read_conf_file(path):
    with open(SERVER_CONF_PATH, 'rt') as conf_file:
        conf_data = load(conf_file)
    global MACHINE_ADDRESS, USERNAME, PASSWORD, MACHINE_URL
    MACHINE_ADDRESS = conf_data['MACHINE_ADDRESS']
    USERNAME = conf_data['USERNAME']
    PASSWORD = conf_data['PASSWORD']
    MACHINE_URL = f"https://{MACHINE_ADDRESS}/"


def validate_argv(argv):
    if len(argv) < 2:
        print(f"missing IntelliCheck search\npython3 importIC.py Signaure Search")
        exit(41)


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


def get_matching_signatures(signature_search,all_signatures):

    matching_signatures = [sig for sig in all_signatures.json() if all([search.lower() in sig["name"].lower() for search in signature_search])]

    return matching_signatures


def get_signature_data(signature_search,matching_signatures):
    if len(matching_signatures) == 0:
        print(f"no signature matching the search: {signature_search} was found {MACHINE_ADDRESS}")
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


def request_signature_commands(session_id,sess):
    # due to what seems to be a bug, the sessionCommands always seem to be empty
    # so in order to get them we will use another API call using the sessionId we fetched
    return sess.get(MACHINE_URL + f"rest/data/integrator/session/commands/{session_id}",headers={"Accept":"application/json"}).text


def add_data_to_map_file(signature_name,signature_sessionId,signature_id,file_name):
    # before saving file, insert file name, signature original name and machine to map file
    with open(SIGNATURE_DATA_FILE, 'r+') as map_file:
        map_data = map_file.readlines()
        is_new_sig = True
        if signature_name in [sig_data.split(' | ')[0] for sig_data in map_data]:
            print('Notice: signature with matching name was imported in the past, do you want to continue? ')
            inp = ''
            while inp not in ['y','n']:
                inp = input('[y/n]: ').lower()

            if inp == 'n':
                print('Exiting')
                exit(45)

            else:
                is_new_sig = False

        if is_new_sig:
            new_data_mapping = '\n' + signature_name + ' | ' + file_name + ' | ' + MACHINE_ADDRESS + ' | ' + str(signature_sessionId) + ' | '+ str(signature_id)
            map_file.write(new_data_mapping)


def write_signature_to_file(signature_name,signature_sessionId,signature_id,commands):
    # remove characters that cause issues in file names
    bad_chars = ['>',':','/','*','\\','<',':','|','?']
    for char in bad_chars:
        file_name = signature_name.replace(char,"")
    file_path = SAVE_PATH + file_name + '.icc'

    add_data_to_map_file(signature_name,signature_sessionId,signature_id,file_name)

    write_to_file(file_path, commands)

    print(file_path + ' was saved successfully')
    return file_path


def import_signature(signature_search):
    read_conf_file(SERVER_CONF_PATH)

    print("server: " + MACHINE_ADDRESS + "\n")

    sess = backbox_login()

    all_signatures = sess.get(MACHINE_URL+"rest/data/intelliChecks/signatures/0/true",headers={"Accept":"application/json"})

    matching_signatures = get_matching_signatures(signature_search,all_signatures)

    signature_data = get_signature_data(signature_search,matching_signatures)
    #ic(signature_data)

    signature_commands = request_signature_commands(signature_data['sessionId'],sess)
    #ic(signature_commands)

    # THIS IS FOR TESTING WAITFOR ON compiler.py 
    #write_to_file('waitfor',signature_commands)

    signature_file_path = write_signature_to_file(signature_data["name"],signature_data['sessionId'],signature_data['id'],signature_commands)

    return {'sig_file_path': signature_file_path}


def main():
    validate_argv(argv)

    import_signature(argv[1:])



if __name__ == "__main__":
    main()

