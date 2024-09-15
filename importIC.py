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
from json import load
import icylib


def validate_argv(argv):
    if len(argv) < 2:
        print(f"missing IntelliCheck search\npython3 importIC.py Signaure Search")
        exit(41)


def get_matching_signatures(signature_search,all_signatures):

    matching_signatures = [sig for sig in all_signatures.json() if all([search.lower() in sig["name"].lower() for search in signature_search])]

    return matching_signatures


def get_signature_data(signature_search,matching_signatures):
    if len(matching_signatures) == 0:
        print(f"no signature matching the search: {signature_search} was found {conf.machine_ip}")
        exit(44)

    elif len(matching_signatures) == 1:
        return matching_signatures

    else:
        signature_names = sorted([sig["name"] for sig in matching_signatures])
        index = 1
        for name in signature_names:
            print(f"[{index}] {name}")
            index += 1

        print(f"please pick signature using it's index (1-{index-1} or 'a' for all)")

        while True:
            picked_index = input()

            if picked_index.strip() == 'a':
                return matching_signatures

            try:
                picked_index = int(picked_index)

            except Exception as e:
                print("index picked is not a number, try again")
                continue

            if picked_index < 1 or picked_index > index-1:
                print("index picked is out of range, try again")

            else:
                return [sig for sig in matching_signatures if sig["name"] == signature_names[picked_index-1]]


def request_signature_commands(session_id,sess):
    # due to what seems to be a bug, the sessionCommands always seem to be empty
    # so in order to get them we will use another API call using the sessionId we fetched
    return sess.get(conf.machine_url + f"rest/data/integrator/session/commands/{session_id}",headers={"Accept":"application/json"}).text


def add_data_to_map_file(signature_name,signature_sessionId,signature_id,file_name,verification):
    with open(icylib.MAP_FILE_PATH, 'r+') as map_file:
        map_file_data = map_file.readlines()
        is_new_sig = True
        if signature_name in [sig_data.split(' | ')[0] for sig_data in map_file_data] and verification:
            print('Notice: signature with matching name was imported in the past, do you want to continue? ')
            inp = ''
            while inp not in ['y','n']:
                inp = input('[y/n]: ').lower()

            if inp == 'n':
                print('Exiting')
                exit(45)

            else:
                is_new_sig = False

        new_data_mapping = signature_name + ' | ' + file_name + ' | ' + conf.machine_ip + ' | ' + str(signature_sessionId) + ' | '+ str(signature_id) + '\n'
        # add new signature map data
        if is_new_sig:
            map_file_data.append(new_data_mapping)
            map_file.writelines(map_file_data)

        # modify signature map data
        else:
            try:
                signature_map_line_index = [line_index for line_index, sig_data in enumerate(map_file_data) if signature_name == sig_data.split(' | ')[0]][0]
            except Exception:
                # should never return Exception, as this will only be reached after finding signature name in map file
                print(f"Logical error: Signature name found in map file, yet when trying to modify it, the same signature name was not found in the map file.\nSignature name: {signature_name}")
                exit(49)

            map_file_data[signature_map_line_index] = new_data_mapping
            map_file.writelines(map_file_data)


def write_signature_to_file(signature_name,signature_sessionId,signature_id,commands,verification):
    # remove characters that cause issues in file names
    bad_chars = ['>',':','/','*','\\','<',':','|','?']
    file_name = signature_name
    for char in bad_chars:
        file_name = file_name.replace(char,"")
    file_path = icylib.ICC_PATH + file_name + '.icc'

    add_data_to_map_file(signature_name,signature_sessionId,signature_id,file_name,verification)

    icylib.write_to_file(file_path, commands)

    print(f"saved successfully:\t{file_path}\n")
    return file_path


def import_signature(signature_search):
    global conf
    conf = icylib.read_conf_file()

    print("server: " + conf.machine_ip + "\n")

    sess = icylib.backbox_login(conf)

    all_signatures = sess.get(conf.machine_url+"rest/data/intelliChecks/signatures/0/true",headers={"Accept":"application/json"})

    matching_signatures = get_matching_signatures(signature_search,all_signatures)

    signature_data_list = get_signature_data(signature_search,matching_signatures)
    #ic(signature_data)

    verification = len(signature_data_list) == 1
    # should we prompt the user if to download the signature if it was already downloaded in the past
    # if we do batch icyget, disable verification
    signature_file_path_list = []
    for signature_data in signature_data_list:
        signature_commands = request_signature_commands(signature_data['sessionId'],sess)
        #ic(signature_commands)

        # THIS IS FOR TESTING WAITFOR ON compiler.py 
        #write_to_file('waitfor',signature_commands)

        signature_file_path_list.append(write_signature_to_file(signature_data["name"],signature_data['sessionId'],signature_data['id'],signature_commands,verification))



    return {'sig_file_path_list': signature_file_path_list}


def main():
    validate_argv(argv)

    import_signature(argv[1:])



if __name__ == "__main__":
    main()
